%if %{_use_internal_dependency_generator}
%define __noautoreq 'perl\\(Filesys::DiskSpace\\)|perl\\(Statistics::Descriptive\\)|perl\\(SNMP\\)|perl\\(IO::File\\)|perl\\(LWP::Parallel::UserAgent\\)|perl\\(-Dopt\\)|perl\\(Net::SNPP\\)|perl\\(Math::TrulyRandom\\)'
%else
%define _requires_exceptions perl(Filesys::DiskSpace)\\|perl(Statistics::Descriptive)\\|perl(SNMP)\\|perl(IO::File)\\|perl(LWP::Parallel::UserAgent)\\|perl(-Dopt)\\|perl(Net::SNPP)
%endif

%define moncgi_version 1.52
%define realname Mon

Summary:	A general-purpose resource monitoring system
Name:		mon
Version:	1.2.0
Release:	21
License:	GPLv2+
Group:		System/Servers
Url:		http://www.kernel.org/software/mon/
Source0:	ftp://ftp.kernel.org/pub/software/admin/mon/%{name}-%{version}.tar.gz
Source1:	%{name}.cf
Source2:	ftp://ftp.kernel.org/pub/software/admin/mon/contrib/cgi-bin/mon.cgi/%{name}.cgi-%{moncgi_version}.tar.bz2
Source3:	ftp://ftp.kernel.org/pub/software/admin/mon/contrib/all-alerts.tar.bz2
Patch0:		mon-1.2.0-init.patch
BuildRequires:	pkgconfig(libtirpc)
# (blino) Authen::PAM use is catched in an eval, but mandatory
Requires:	perl-Authen-PAM
Requires:	fping

%description
Mon is a general-purpose resource monitoring system.  It can be used
to monitor network service availability, server problems,
environmental conditions (i.e., the temperature in a room) or other
things. Mon can be used to test the condition and/or to trigger an
action upon failure of the condition.  Mon keeps the testing and
action-taking tasks as separate, stand-alone programs.

Mon is very extensible.  Monitors and alerts are not a part of mon, but
the distribution comes with a handful of them to get you started. This
means that if a new service needs monitoring, or if a new alert is
required, the mon server will not need to be changed.

%prep
%setup -q -a 2 -a 3
%apply_patches

%build
%serverbuild
export RPM_OPT_FLAGS="%{optflags} -DUSE_VENDOR_CF_PATH=1"

%make -C mon.d LDLIBS=-ltirpc

%install
mkdir -p %{buildroot}/%{_bindir}
install -m 755 mon %{buildroot}/%{_bindir}
install -m 755 clients/moncmd %{buildroot}/%{_bindir}
install -m 755 clients/monshow %{buildroot}/%{_bindir}
install -m 755 clients/skymon/skymon %{buildroot}/%{_bindir}

# man
mkdir -p %{buildroot}%{_mandir}/{man1,man8}
install -m 644 doc/*.1 %{buildroot}%{_mandir}/man1
install -m 644 doc/*.8 %{buildroot}%{_mandir}/man8

mkdir -p %{buildroot}/%{_libdir}/mon/alert.d
install -m 755 alert.d/* %{buildroot}/%{_libdir}/mon/alert.d
find alerts/  -type f ! -regex ".*~" ! -regex ".*README"  -exec install -m 755 {} %{buildroot}/%{_libdir}/mon/alert.d  \;

mkdir -p %{buildroot}/%{_var}/lib/mon/state.d
mkdir -p %{buildroot}/%{_var}/lib/mon/log.d

mkdir -p %{buildroot}/%{_libdir}/mon/mon.d
install -m 755 mon.d/*.monitor %{buildroot}/%{_libdir}/mon/mon.d
install -m 755 mon.d/dialin.monitor.wrap %{buildroot}/%{_libdir}/mon/mon.d

#chmod 644 %{buildroot}/%{_libdir}/mon/mon.d/{Makefile,*.c}

mkdir -p %{buildroot}/%{_sysconfdir}/mon
install -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/mon/mon.cf
install -m 644 etc/auth.cf %{buildroot}%{_sysconfdir}/mon/auth.cf
echo "# user: passwd" > %{buildroot}%{_sysconfdir}/mon/userfile

mkdir -p %{buildroot}%{_initrddir}
cp -f etc/S99mon %{buildroot}%{_initrddir}/mon

mkdir -p %{buildroot}/%{_var}/www/cgi-bin/
mv mon.cgi-%{moncgi_version}/mon.cgi mon.cgi
install -m 755 mon.cgi %{buildroot}/%{_var}/www/cgi-bin/

# doc
chmod 644 {README*,doc/README*}
echo "%doc `find alerts/  -type f ! -regex ".*~" -name "*README" | xargs`"> alerts.README

%post
%_post_service mon

%preun
%_preun_service mon

%files -f alerts.README
%doc CHANGES CREDITS COPYRIGHT README INSTALL TODO doc/README.*
%doc KNOWN-PROBLEMS VERSION utils/*
%doc etc/*.cf etc/example.m4 etc/example.monshowrc clients/{skymon,batch-example}
%doc mon.cgi-1.52/
%dir %config(noreplace) %{_sysconfdir}/mon
%config(noreplace) %{_sysconfdir}/mon/*.cf
%attr (0600,root,root) %config(noreplace) %{_sysconfdir}/mon/userfile
%config(noreplace) %{_initrddir}/mon
%{_mandir}/*/*
%{_var}/www/cgi-bin/mon.cgi
%{_bindir}/mon
%{_bindir}/monshow
%{_bindir}/moncmd
%{_bindir}/skymon
%{_libdir}/mon/alert.d
%{_libdir}/mon/mon.d/*.monitor
%attr(02555,root,dialout) %{_libdir}/mon/mon.d/dialin.monitor.wrap
%dir %{_var}/lib/mon
%dir %{_var}/lib/mon/state.d
%dir %{_var}/lib/mon/log.d

