#
# TODO:
# - more clean init script ? (especially asa.sh) but usable,

Summary:	Jabber server component agent for sending SMS messages
Summary(pl.UTF-8):	Komponent serwera Jabbera do wysyłania wiadomości SMS
Name:		asa
Version:	0.1.7
Release:	2
License:	GPL
Group:		Applications/Communications
Source0:	http://www.apatsch.wroc.biz/asa/%{name}-%{version}.tar.gz
# Source0-md5:	2a754e9ab1220f79060a68a46a76cc6c
Source1:	jabber-%{name}-transport.init
Source2:	%{name}.sh
# This patch updates asa to recent version from SVN (kg doesn't releases tarball)
Patch0:		%{name}-svn-26-05-2007.patch
Patch1:		%{name}-PLD.patch
Patch2:		%{name}-userrun.patch
Patch3:		%{name}-lib64.patch
URL:		http://www.apatsch.wroc.biz/asa/
BuildRequires:	rpm-perlprov
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post):	/usr/bin/perl
Requires(post):	sed >= 4.0
Requires(post,preun):	/sbin/chkconfig
Requires(pre):	jabber-common
Requires:	jabberd >= 1.4
Requires:	perl-Crypt-SSLeay
Requires:	perl-Unicode-Lite
Requires:	perl-Unicode-Map
Requires:	perl-Unicode-String
Requires:	perl-libwww
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
ApaSMSAgent - Jabber server component agent for sending SMS messages
to cellular networks. Targetted at polish users, but can be adopted
for international use, because of it's plugin-based architecture.

%description -l pl.UTF-8
ApaSMSAgent - komponent serwera Jabbera umożliwiający wysyłanie
wiadomości SMS do sieci komórkowych. Aktualnie obsługuje głównie
polskie sieci, ale z łatwością może zostać rozszerzony o inne dzięki
modularnej budowie opartej na wtyczkach.

%prep
%setup -q
%patch -P0 -p1
%patch -P1 -p0
%patch -P2 -p1
%if "%{_lib}" == "lib64"
%patch -P3 -p1
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/jabber,%{_sbindir},/etc/rc.d/init.d,/var/lib/jabber/asa/storage,%{_libdir}/jabber/asa/plugins}

install config.xml $RPM_BUILD_ROOT%{_sysconfdir}/jabber/asa.xml
install ApaSMSAgent.pl $RPM_BUILD_ROOT%{_sbindir}
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/jabber-asa-transport
install %{SOURCE2} $RPM_BUILD_ROOT%{_sbindir}
install plugins/*.pl $RPM_BUILD_ROOT%{_libdir}/jabber/asa/plugins/

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -f %{_sysconfdir}/jabber/secret ] ; then
	SECRET=`cat %{_sysconfdir}/jabber/secret`
	if [ -n "$SECRET" ] ; then
		echo "Updating component authentication secret in asa.xml..."
		%{__sed} -i -e "s/>secret</>$SECRET</" /etc/jabber/asa.xml
	fi
fi
/sbin/chkconfig --add jabber-asa-transport
%service jabber-asa-transport restart "Jabber ASA transport"

%preun
if [ "$1" = "0" ]; then
	%service jabber-asa-transport stop
	/sbin/chkconfig --del jabber-asa-transport
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog AUTHORS README
%attr(755,root,root) %{_sbindir}/*
%attr(640,root,jabber) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/jabber/asa.xml
%attr(754,root,root) /etc/rc.d/init.d/jabber-asa-transport
%attr(770,root,jabber) /var/lib/jabber
%dir %{_libdir}/jabber
%dir %{_libdir}/jabber/asa
%attr(755,root,root) %{_libdir}/jabber/asa/plugins
