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
Release:	14
Source0:	ftp://ftp.kernel.org/pub/software/admin/mon/%{name}-%{version}.tar.gz
Source1:	%{name}.cf
Source2:	ftp://ftp.kernel.org/pub/software/admin/mon/contrib/cgi-bin/mon.cgi/%{name}.cgi-%{moncgi_version}.tar.bz2
Source3:	ftp://ftp.kernel.org/pub/software/admin/mon/contrib/all-alerts.tar.bz2
Patch0:		mon-1.2.0-init.patch
Url:		http://www.kernel.org/software/mon/
License:	GPLv2+
Group:		System/Servers
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
%patch0 -p1

%build
%serverbuild
export RPM_OPT_FLAGS="%{optflags} -DUSE_VENDOR_CF_PATH=1"

%make -C mon.d

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



%changelog
* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 1.2.0-10mdv2011.0
+ Revision: 666476
- mass rebuild

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 1.2.0-9mdv2011.0
+ Revision: 606655
- rebuild

* Wed Mar 17 2010 Oden Eriksson <oeriksson@mandriva.com> 1.2.0-8mdv2010.1
+ Revision: 523355
- rebuilt for 2010.1

* Thu Sep 03 2009 Christophe Fergeau <cfergeau@mandriva.com> 1.2.0-7mdv2010.0
+ Revision: 426162
- rebuild

* Fri Jan 09 2009 Frederic Crozat <fcrozat@mandriva.com> 1.2.0-6mdv2009.1
+ Revision: 327545
- replace uucp by dialout group

* Tue Jun 17 2008 Thierry Vignaud <tv@mandriva.org> 1.2.0-5mdv2009.0
+ Revision: 223300
- rebuild

* Wed Jan 23 2008 Thierry Vignaud <tv@mandriva.org> 1.2.0-4mdv2008.1
+ Revision: 157256
- rebuild with fixed %%serverbuild macro

* Tue Jan 15 2008 Thierry Vignaud <tv@mandriva.org> 1.2.0-3mdv2008.1
+ Revision: 153201
- rebuild
- rebuild
- kill re-definition of %%buildroot on Pixel's request

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

* Thu Sep 06 2007 Adam Williamson <awilliamson@mandriva.org> 1.2.0-1mdv2008.0
+ Revision: 80606
- use Fedora license policy
- rediff patch0
- new release 1.2.0

* Fri Jun 01 2007 Adam Williamson <awilliamson@mandriva.org> 1.0.0pre5-1mdv2008.0
+ Revision: 33555
- rediff patch
- new release 1.0.0pre5, rebuild for new era


* Tue Mar 22 2005 Olivier Blin <oblin@mandrakesoft.com> 0.99.2-5mdk
- require perl-Authen-PAM (not automatically computed, #12682)
- require fping (#12690)
- fix summary ended with dot

* Mon Aug 11 2003 Damien Chaumette <dchaumette@mandrakesoft.com> 0.99.2-4mdk
- remove requires
- stick to #!/usr/bin/perl in each file
- add _requires_exceptions

* Tue Jul 22 2003 Per Øyvind Karlsen <peroyvind@sintrax.net> 0.99.2-3mdk
- rebuild
- drop Prefix tag
- prereq on rpm-helper
- bzip2 P0

* Tue Mar 12 2002 Philippe Libat <philippe@mandrakesoft.com> 0.99.2-2mdk
- require

* Fri Dec 07 2001 Philippe Libat <philippe@mandrakesoft.com> 0.99.2-1mdk
- New version: 0.99.2
- add contrib/all-alerts

* Mon Aug 27 2001 Philippe Libat <philippe@mandrakesoft.com> 0.99.1-1mdk
- new version

* Tue May 08 2001 Guillaume Cottenceau <gc@mandrakesoft.com> 0.38.21-1mdk
- version 0.38.21

* Wed Sep 27 2000 Philippe Libat <philippe@mandrakesoft.com> 0.38.20-8mdk
- use post_service and preun_service macros
- use serverbuild macro

* Wed Sep 27 2000 Philippe Libat <philippe@mandrakesoft.com> 0.38.20-7mdk
- change Requires

* Fri Sep 22 2000 Philippe Libat <philippe@mandrakesoft.com> 0.38.20-6mdk
- change /home/httpd to /var/www

* Wed Sep 20 2000 Philippe Libat <philippe@mandrakesoft.com> 0.38.20-5mdk
- in mon.cf change statedir, logdir, dtlogfile location
- add preun condition

* Wed Sep 13 2000 Philippe Libat <philippe@mandrakesoft.com> 0.38.20-4mdk
- var/lib/mon/

* Tue Sep 12 2000 Philippe Libat <philippe@mandrakesoft.com> 0.38.20-3mdk
- start in background
- monitor ping

* Mon Sep 11 2000 Philippe Libat <philippe@mandrakesoft.com> 0.38.20-2mdk
- not active in post

* Thu Aug 31 2000 Philippe Libat <philippe@mandrakesoft.com> 0.38.20-1mdk
- upgraded to 0.38.20
- macroszifications.

* Fri Jun 30 2000 Nicolas Planel <nicolas@mandrakesoft.com>
- spec file for MandrakeSoft

* Tue Feb 15 2000 Tim Powers <timp@redhat.com>
- Requires: Mon should have been Requires: perl-Mon, fixed
- built for 6.2
- BuildArch is noarch

* Mon Feb 14 2000 Andrew Anderson <andrew@redhat.com>
- point the cgi script to localhost
- sample config file cleanup

* Sat Feb 12 2000 Andrew Anderson <andrew@redhat.com>
- Re-introduced dependancy for Mon
- cleaned up init script
- fix bogus /var/run/mon.pid directory

* Thu Nov 18 1999 Tim Powers <timp@redhat.com>
- updated to 0.38.15
- removed Requires: perl-Mon

* Mon Aug 16 1999 Bill Nottingham <notting@redhat.com>
- fix bogus requires.

* Fri Jul 23 1999 Cristian Gafton <gafton@redhat.com>
- make sure we don't end up owning dirs that aren't ours
- updated the Requires lines

* Mon Jul 19 1999 Tim Powers <timp@redhat.com>
- updated source to 0.38.13
- built for 6.1

* Thu Apr 15 1999 Michael Maher <mike@redhat.com>
- built package for 6.0
- pre release is out, but stayed with stable one

* Wed Sep 09 1998 Michael Maher <mike@redhat.com>
- built package

