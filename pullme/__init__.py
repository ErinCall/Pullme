import sys
import os
import re
import urllib2
import optparse
import json
import getpass
import base64

from pullme.subprocess_wrapper import Subprocess as subprocess
from pullme.git import Git as git
from pullme.interaction import Interaction as interaction

def main():
    settings = load_settings()
    check_outstanding_changes(settings)
    head_branch = determine_head_branch()
    push_to_personal(settings, head_branch)
    base_branch = determine_base_branch(settings)
    upstream_github_path = github_path_from_remote_name(settings['upstream'])
    personal_github_path = github_path_from_remote_name(settings['personal'])
    make_pull_request(settings, upstream_github_path, personal_github_path, base_branch, head_branch)

def check_outstanding_changes(settings):
    if settings['assume']:
        return
    if git.has_outstanding_changes():
        git.show_outstanding_changes()
        interaction.confirm_continue(settings, 'There are outstanding changes.')

def load_settings():
    settings = {}
    password_file = '%s/.githubpass' % os.environ['HOME']
    if not os.path.exists(password_file):
        establish_password_file(password_file)
    settings['password'] = load_password(password_file)

    parser = optparse.OptionParser(
        description="""
Submit a pull request for the currently-checked-out branch. Particularly
targeted at working with long-running feature branches, pullme tries to guess
what branch you want your code pulled into. Contrast with Github's system of
defining a "base branch" and pointing all pull requests at that by default.
""",
        epilog="""
These options can also be set using `git config [--global] pullme.SETTING VALUE`.
(Though this may sometimes be improper)
"""
    )

    setters = []
    setters.append(add_setting(parser, 'upstream', 'origin', {
        'help': "The remote-name for the repo into which you want your code pulled. Defaults to 'origin'."
    }))
    setters.append(add_setting(parser, 'personal', os.environ['USER'], {
        'help': 'The remote-name for your fork on github. Defaults to $USER.'
    }))
    setters.append(add_setting(parser, 'assume', False, {
        'action': 'store_true',
        'help': 'Proceed on assumptions without confirming them.'
    }))
    setters.append(add_setting(parser, 'file', None, {
        'help': 'Read the pull request title and body from FILE, rather than invoking $EDITOR'
    }))
    setters.append(add_setting(parser, 'issue', None, {
        'help': 'Have github generate a title and body using an issue number',
    }))
    setters.append(add_setting(parser, 'open', False, {
        'action': 'store_true',
        'help': 'Open the pull request URL using "open". Mac OS X specific.'
    }))
    (options, args) = parser.parse_args()
    for setter in setters:
        setter(settings, options)
    return settings

def add_setting(parser, name, default, parser_kwargs):
    parser.add_option('-' + name[0], '--' + name, **parser_kwargs)
    def setter(settings, options):
        settings[name] = git.config(name)
        if getattr(options, name) is not None:
            settings[name] = getattr(options, name)
        if not settings.get(name):
            settings[name] = default
    return setter

def establish_password_file(password_filename):
    print """Looks like this is your first run. Enter your GitHub password (we'll infer your
github username from your personal branch)."""

    password = getpass.getpass('Password: ', sys.stderr)
    openflags = os.O_RDWR | os.O_CREAT | os.O_EXCL
    fd = os.open(password_filename, openflags, 0600)
    fh = os.fdopen(fd, 'w')

    fh.write(password)
    fh.close()

def load_password(password_filename):
    password_file = open(password_filename, 'r')
    password = password_file.readline()
    password_file.close()
    return password

def determine_head_branch():
    return git.current_branch()

def push_to_personal(settings, branch):
    correct = interaction.confirm_assumptions(settings,
        'Do you want to push to %s/%s?' % (settings['personal'], branch),
        'To what %s would you like to push? ',
        remote=settings['personal'],
        branch=branch,
    )
    settings['personal'] = correct['remote']
    git.push_to_personal(settings['personal'], correct['branch'])

def determine_base_branch(settings):
# look for the most recent reachable commit that has a corresponding ref name
# on upstream, and return it.
    print 'looking for an appropriate base branch'

    ref_names = git.log_with_ref_names()

    remote = settings['upstream']
    upstream_ref_line = ''
    while not upstream_ref_line and ref_names.poll() is None:
        line = ref_names.stdout.readline()
        if re.search('refs/remotes/%s' % remote, line):
            upstream_ref_line = line.strip()
    ref_names.stdout.close()
    if ref_names.poll():
        exit(ref_names.poll())
    del ref_names
    base_branch = extract_branch_name(upstream_ref_line, remote)

    if has_multiple_branches(upstream_ref_line, remote) or not base_branch:
        print 'Could not automatically determine base branch. What branch should we use?'
        base_branch = raw_input("Branch: ")

    correct = interaction.confirm_assumptions(settings,
        'Do you want to submit a pull request to %s/%s?' % (remote, base_branch),
        'To what %s would you like to submit your request? ',
        branch=base_branch,
    )
    return correct['branch']

def extract_branch_name(ref_line, remote):
    if ref_line is None:
        return None
    extractor_regex = r'.*refs/remotes/%s/(?!HEAD)(?P<base_branch>.*?)(?:\)$|, ).*' % remote
    match = re.search(extractor_regex, ref_line)
    return match.groupdict()['base_branch'] if match else None

def has_multiple_branches(ref_line, remote):
    if ref_line is None:
        return None
    extractor_regex = r'(?:refs/remotes/%s/(?!HEAD).*){2,}' % remote
    return bool(re.search(extractor_regex, ref_line))

def github_path_from_remote_name(remote):
    remotes_info = git.remotes()
    fork_url = filter(lambda x: re.search('fetch', x),
               filter(lambda x: re.search(remote, x),
               remotes_info))[0]
#now we have a thing that looks like one of these:
#origin  git@github.com:andrewlorente/audience.git (fetch)
#origin  git@github.com:andrewlorente/audience (fetch)
#origin  https://github.com/andrewlorente/audience.git (fetch)
#origin  https://github.com/andrewlorente/audience/ (fetch)
#origin  https://github.com/andrewlorente/audience (fetch)
    match = re.search(r'.*github.com[:/](?P<path>.*?)(?:\.git|/)? \(fetch\).*', fork_url)
    if not match:
        sys.stderr.write("Couldn't determine a github path from '%s' (this is "
                        "probably a bug in the script; sorry)" % fork_url)
        exit(1)
    return match.groupdict()['path']

def make_pull_request(settings, upstream_github_path,
                    personal_github_path, base_branch, head_branch):

    description = {}
    if settings['issue']:
        description = {'issue': settings['issue']}
    else:
        title, body = get_description(settings, base_branch)
        description = {'title': title, 'body': body}
    url = 'https://api.github.com/repos/%s/pulls' % upstream_github_path
    print 'pulling to %s' % url
    username = personal_github_path.split('/')[0]
    data = {
        'head': '%s:%s' % (username, head_branch),
        'base': base_branch,
    }
    data.update(description)
    request = urllib2.Request(url, data=json.dumps(data))
    auth = base64.b64encode('%s:%s' % (username, settings['password']))
    request.add_header('Authorization', 'Basic %s' % auth)
    try:
        response = json.loads(urllib2.urlopen(request).read())
        print "Successfully opened pull request #%s" % response['number']
        print response['html_url']
        if settings['open']:
            subprocess.check_output(['open', response['html_url']])
    except urllib2.HTTPError, e:
        error = json.loads(e.read())
        sys.stderr.write("Pull request failed:\n")
        sys.stderr.write(error['message'] + "\n")
        for sub_error in error.get('errors', []):
#The github API has handed back errors structured in at least two ways so far.
#Will it come up with a third way? Hope not...
            if 'message' in sub_error:
                sys.stderr.write(sub_error['message'] + "\n")
            elif 'value' in sub_error:
                sys.stderr.write("%s %s: '%s'" % (
                    sub_error['code'],
                    sub_error['field'],
                    str(sub_error['value']),
                ))
            else:
                sys.stderr.write("""The github api has returned an error that I don't know how to handle. Be a dear
and open an issue? https://github.com/AndrewLorente/PullMe/issues/new
Please include this JSON:
%s
""" % json.dumps(error))
                exit(1)

def get_description(settings, base_branch, filename=None):
    filename = filename or settings['file']
    if not filename:
        filename = generate_description_file(settings, base_branch)
        edit_file(filename)

    pull_message_file = open(filename, 'r')
    title, body = read_description_from_file(pull_message_file)
    pull_message_file.close()

    if not title:
        confirmation_settings = settings.copy()
        confirmation_settings['assume'] = False
        interaction.confirm_continue(
            confirmation_settings,
            "I couldn't find a pull request title."
        )
        edit_file(filename)
        return get_description(settings, base_branch, filename=filename)

    if not settings['file']:
        os.remove(filename)

    return title, body

def generate_description_file(settings, base_branch):
    filename = 'pullme_description'
    pull_message_file = open(filename, 'w')
    commits = git.commits_since('%s/%s' % (settings['upstream'], base_branch))
    if len(commits) == 1:
        #If there is a single commit, dump its commit message
        #into the description file
        pull_message_file.write(git.latest_commit_message())

    pull_message_file.write("""


#put your pull request message here.
#As with a git commit message, the first line is the title, then there is a
#blank line, and any subsequent lines are description.
#lines starting with a hash are comments.
#commits in this pull:
#
""")
    for line in commits:
        pull_message_file.write("#" + line)
    pull_message_file.flush()
    pull_message_file.close()

    return filename

def edit_file(filename):
    editor = os.environ.get('EDITOR', '/bin/ed')
    subprocess.check_call([editor, filename])

def read_description_from_file(description_file):
    title = description_file.readline().strip()
    description_file.readline()
    body = ''
    for line in description_file:
        if re.match('^[^#]', line):
            body += line.rstrip() + "\n"

    return title, body.rstrip()

exit = sys.exit
