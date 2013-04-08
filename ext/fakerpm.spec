Name:           fakerpm
Version:        0.1.0
Release:        1%{?dist}
Group:          Utilities
Summary:        A command-line utility for creating "fake" RPMs for testing purposes

License:        BSD  
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  make >= 3.81
BuildRequires:  coreutils
Requires:       rpm
Requires:       rpm-build
Requires:       python2
BuildArch:      noarch

%description
A command-line utility for creating "fake" RPMs for the purposes of testing
RPM dependencies.

%prep
%setup -q -c

%install
[ -d $RPM_BUILD_ROOT ] && rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT

make DESTDIR=$RPM_BUILD_ROOT install

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(0644,root,root,0755)
%attr(0755,root,root) %{_bindir}/fakerpm
%{_datadir}/fakerpm/*

%changelog
* Wed Mar 27 2013 - Jon McKenzie - 0.1.0
- Initial implementation
