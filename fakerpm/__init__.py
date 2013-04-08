#!/usr/bin/env python

import os
import optparse
import string
import tempfile
import subprocess
import shlex

SPEC_TEMPLATE = """
Name:           ${name}
Version:        ${version}
Release:        ${release}
Summary:        ${summary}
Group:          ${group}
License:        Fake License
URL:            http://www.fake.rpm
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
${build_arch_field}
${build_requires_fields}
${provides_fields}
${requires_fields}

%description
${description}

%prep
%build
%install
%clean

%files

%changelog
* Thu Jan 1 2000 Nobody
- Wrote this sweet spec file

"""
DEFAULT_GROUP = 'Development/Build Tools'
DEFAULT_SUMMARY = 'This is a fake RPM that does nothing!'
DEFAULT_DESCRIPTION = DEFAULT_SUMMARY
DEFAULT_VERSION = '1.0.0'
DEFAULT_RELEASE = '1.el5'

class FakeSpecTemplate(string.Template):
    spec_template = SPEC_TEMPLATE

    def __init__(self, 
        name,
        group = DEFAULT_GROUP,
        summary = DEFAULT_SUMMARY,
        description = DEFAULT_DESCRIPTION,
        version = DEFAULT_VERSION,
        release = DEFAULT_RELEASE,
        arch = None,
        provides = [],
        requires = [],
        build_requires = [],
    ):
        self.name = name
        self.group = group
        self.summary = summary
        self.description = description
        self.version = version
        self.release = release
        self.arch = arch
        self.provides = provides
        self.requires = requires
        self.build_requires = build_requires

        string.Template.__init__(self, self.spec_template)

    def substitute(self, mapping = {}, **kwargs):
        if mapping or kwargs:
            substituted = string.Template.substitute(self, mapping, **kwargs)
        else:
            substituted = self._spec_substitute()
        return substituted

    def _spec_substitute(self):
        return self.substitute(
            name = self.name,
            group = self.group,
            summary = self.summary,
            description = self.description,
            version = self.version,
            release = self.release,
            build_arch_field = self._build_build_arch(),
            provides_fields = self._build_provides(),
            requires_fields = self._build_requires(),
            build_requires_fields = self._build_build_requires(),
        )

    def _build_build_arch(self):
        if self.arch:
            return "BuildArch:\t%s\n" % self.arch
        else:
            return ""
    def _build_provides(self):
        return "\n".join([ ("Provides:\t%s" % i) for i in self.provides ]) + "\n"
    def _build_build_requires(self):
        return "\n".join([ ("BuildRequires:\t%s" % i) for i in self.build_requires ]) + "\n"
    def _build_requires(self):
        return "\n".join([ ("Requires:\t%s" % i) for i in self.requires ]) + "\n"

def create_cli():
    cli = optparse.OptionParser(
        usage = 'usage: %prog [options]',
        description = 'A command-line utility for creating "fake" RPMs for the '
                      'purposes of testing RPM dependencies.',
    )

    build_group = optparse.OptionGroup(cli, "Build Options",
        "Customize how the fake RPM is built")
    build_group.add_option('--dont-build', action='store_true',
        help="Don't actually build anything")
    cli.add_option_group(build_group)

    out_group = optparse.OptionGroup(cli, "Output Options",
        "Customize what's printed to the screen")
    out_group.add_option('--build-output', action='store_true',
        help="Show `rpmbuild' output", default=False)
    out_group.add_option('--print-specfile', action='store_true',
        help="Print the generated spec file")
    cli.add_option_group(out_group)

    attr_group = optparse.OptionGroup(cli, "RPM Attributes",
        "Customize various attributes of the fake RPM")
    #cli.add_option('-s', '--from-spec', metavar='SPECFILE',
    #    help='load attributes from a spec file (overrideable by options below)')
    attr_group.add_option('-n', '--name',
        help='Set the RPM name')
    attr_group.add_option('-g', '--group',
        help='Set the RPM group')
    attr_group.add_option('-S', '--summary',
        help='Set the RPM summary')
    attr_group.add_option('-d', '--description',
        help='Set the RPM description')
    attr_group.add_option('-v', '--version',
        help='Set the RPM version')
    attr_group.add_option('-r', '--release',
        help='Set the RPM release')
    attr_group.add_option('-a', '--arch',
        help='Set the RPM BuildArch (defaults to system architecture)')
    attr_group.add_option('-p', '--provides', metavar='CAPABILITY', action='append',
        help='Add a CAPABILITY to the fake RPM (can specify multiple times)')
    attr_group.add_option('-R', '--requires', metavar='CAPABILITY', action='append',
        help='Require a CAPABILITY (can specify multiple times)')
    attr_group.add_option('-b', '--build-requires', metavar='CAPABILITY', action='append',
        help='Require a build-time dependency (can specify multiple times)')

    cli.add_option_group(attr_group)
    return cli

def run(command, capture_output=True):
    if capture_output:
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE
    else:
        stdout = None
        stderr = None
    proc = subprocess.Popen(shlex.split(command), stderr=stderr, stdout=stdout) 
    stdout, stderr = proc.communicate()
    code = proc.returncode
    return code, stdout, stderr

def load_from_spec(filename):
    pass

def _build_data_from_opts(opts):
    data = {}
    for k in opts.__dict__.keys():
        val = getattr(opts, k)
        if val:
            data[k] = val
    return data

def main(argv=None):
    cli = create_cli()

    opts, args = cli.parse_args(argv)

    if not opts.name:
        cli.error('RPM requires a name (-n/--name)')

    dont_build = opts.dont_build
    build_output = not opts.build_output
    print_specfile = opts.print_specfile
    del opts.__dict__['dont_build']
    del opts.__dict__['build_output']
    del opts.__dict__['print_specfile']

    # populate template with data
    data = _build_data_from_opts(opts)
    template = FakeSpecTemplate(**data)
    specfile_data = template.substitute()

    if print_specfile:
        print specfile_data

    # write the specfile
    specfile = tempfile.NamedTemporaryFile()
    open(specfile.name, 'w').write(specfile_data)

    # build the RPM
    if not dont_build:
        code,_,_ = run('rpmbuild --define "_rpmdir ." --define "_rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm" -ba %s' % specfile.name, capture_output=build_output)
    else:
        code = 0

    raise SystemExit, code
