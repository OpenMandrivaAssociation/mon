%define version 1.2.0
%define moncgi_version 1.52
%define release %mkrel 1
%define name mon
%define realname Mon

Summary: A general-purpose resource monitoring system
Name: %{name}
Version: %{version}
Release: %{release}
Source0: ftp://ftp.kernel.org/pub/software/admin/mon/%{name}-%{version}.tar.gz
Source1: %{name}.cf
Source2: ftp://ftp.kernel.org/pub/software/admin/mon/contrib/cgi-bin/mon.cgi/%{name}.cgi-%{moncgi_version}.tar.bz2
Source3: ftp://ftp.kernel.org/pub/software/admin/mon/contrib/all-alerts.tar.bz2
Patch0: mon-1.2.0-init.patch
Url: http://www.kernel.org/software/mon/
License: GPLv2+
Group: System/Servers
Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-root/
# (blino) Authen::PAM use is catched in an eval, but mandatory
Requires: perl-Authen-PAM
Requires: fping
%define _requires_exceptions perl(Filesys::DiskSpace)\\|perl(Statistics::Descriptive)\\|perl(SNMP)\\|perl(IO::File)\\|perl(LWP::Parallel::UserAgent)\\|perl(-Dopt)\\|perl(Net::SNPP)

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
%patch0 -p1

%build
%serverbuild
export RPM_OPT_FLAGS="$RPM_OPT_FLAGS -DUSE_VENDOR_CF_PATH=1"

%make -C mon.d

%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT/%{_bindir}
install -m 755 mon $RPM_BUILD_ROOT/%{_bindir}
install -m 755 clients/moncmd $RPM_BUILD_ROOT/%{_bindir}
install -m 755 clients/monshow $RPM_BUILD_ROOT/%{_bindir}
install -m 755 clients/skymon/skymon $RPM_BUILD_ROOT/%{_bindir}

# man
mkdir -p $RPM_BUILD_ROOT%{_mandir}/{man1,man8}
install -m 644 doc/*.1 $RPM_BUILD_ROOT%{_mandir}/man1
install -m 644 doc/*.8 $RPM_BUILD_ROOT%{_mandir}/man8

mkdir -p $RPM_BUILD_ROOT/%{_libdir}/mon/alert.d
install -m 755 alert.d/* $RPM_BUILD_ROOT/%{_libdir}/mon/alert.d
find alerts/  -type f ! -regex ".*~" ! -regex ".*README"  -exec install -m 755 {} $RPM_BUILD_ROOT/%{_libdir}/mon/alert.d  \;

mkdir -p $RPM_BUILD_ROOT/%{_var}/lib/mon/state.d
mkdir -p $RPM_BUILD_ROOT/%{_var}/lib/mon/log.d

mkdir -p $RPM_BUILD_ROOT/%{_libdir}/mon/mon.d
install -m 755 mon.d/*.monitor $RPM_BUILD_ROOT/%{_libdir}/mon/mon.d
install -m 555 mon.d/dialin.monitor.wrap $RPM_BUILD_ROOT/%{_libdir}/mon/mon.d

#chmod 644 $RPM_BUILD_ROOT/%{_libdir}/mon/mon.d/{Makefile,*.c}

mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/mon
install -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/mon/mon.cf
install -m 644 etc/auth.cf $RPM_BUILD_ROOT%{_sysconfdir}/mon/auth.cf
echo "# user: passwd" > $RPM_BUILD_ROOT%{_sysconfdir}/mon/userfile


mkdir -p $RPM_BUILD_ROOT%{_initrddir}
cp -f etc/S99mon $RPM_BUILD_ROOT%{_initrddir}/mon

mkdir -p $RPM_BUILD_ROOT/%{_var}/www/cgi-bin/
mv mon.cgi-%{moncgi_version}/mon.cgi mon.cgi
install -m 755 mon.cgi $RPM_BUILD_ROOT/%{_var}/www/cgi-bin/

# doc
chmod 644 {README*,doc/README*}
echo "%doc `find alerts/  -type f ! -regex ".*~" -name "*README" | xargs`"> alerts.README

%clean
rm -rf $RPM_BUILD_ROOT

%post
%_post_service mon

%preun
%_preun_service mon

%files -f alerts.README
%defattr(-,root,root)
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
%{_libdir}/mon
%attr(02555,root,uucp) %{_libdir}/mon/mon.d/dialin.monitor.wrap
%dir %{_var}/lib/mon
%dir %{_var}/lib/mon/state.d
%dir %{_var}/lib/mon/log.d

