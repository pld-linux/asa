#
# TODO:
# - more clean init script ? (especially asa.sh),

%include	/usr/lib/rpm/macros.perl
Summary:	Jabber server component agent for sending SMS messages
Summary(pl):	Komponent serwera Jabbera do wysy³ania wiadomo¶ci SMS
Name:		asa
Version:	0.1.4
Release:	2
License:	GPL
Group:		Applications/Communications
Source0:	http://www.apatsch.wroc.biz/asa/%{name}-%{version}.tar.gz
# Source0-md5:	e2bdce7a80a758fa02aff2cdc39c66b1
Source1:	jabber-asa-transport.init
Source2:	%{name}.sh
Patch0:		%{name}-PLD.patch
Patch1:		%{name}-lib64.patch
Patch2:		%{name}-MiastoPlusa.patch
URL:		http://www.apatsch.wroc.biz/asa/
BuildRequires:	rpm-perlprov
Requires(pre):	jabber-common
Requires(post,preun):	/sbin/chkconfig
Requires(post):	/usr/bin/perl
Requires:	jabberd >= 1.4
Requires:	perl-libwww
Requires:	perl-Unicode-Lite
Requires:	perl-Crypt-SSLeay
Requires:	perl-Unicode-String
Requires:	perl-Unicode-Map
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
ApaSMSAgent - Jabber server component agent for sending
SMS messages to cellular networks. Targetted at polish users,
but can be adopted for international use, because of it's
plugin-based architecture.

%description -l pl
ApaSMSAgent - komponent serwera Jabbera umo¿liwiaj±cy wysy³anie
wiadomo¶ci SMS do sieci komórkowych. Aktualnie obs³uguje g³ównie
polskie sieci, ale z ³atwo¶ci± mo¿e zostaæ rozszerzony o inne dziêki
modularnej budowie opartej na wtyczkach.

%prep
%setup -q
%patch0 -p1
%if "%{_lib}" == "lib64"
%patch1 -p1
%endif
%patch2 -p1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/jabber,%{_sbindir},/etc/rc.d/init.d,/var/lib/jabber/asa/storage,%{_libdir}/jabber/asa/plugins}

install config.xml $RPM_BUILD_ROOT%{_sysconfdir}/jabber/asa.xml
install ApaSMSAgent.pl $RPM_BUILD_ROOT%{_sbindir}
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/jabber-asa-transport
install %{SOURCE2} $RPM_BUILD_ROOT%{_sbindir}
install plugins/*.pl $RPM_BUILD_ROOT/%{_libdir}/jabber/asa/plugins/

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -f /etc/jabber/secret ] ; then
	SECRET=`cat /etc/jabber/secret`
	if [ -n "$SECRET" ] ; then
		echo "Updating component authentication secret in asa.xml..."
		perl -pi -e "s/>secret</>$SECRET</" /etc/jabber/asa.xml
	fi
fi
/sbin/chkconfig --add jabber-asa-transport
if [ -r /var/lock/subsys/jabber-asa-transport ]; then
	/etc/rc.d/init.d/jabber-asa-transport restart >&2
else
	echo "Run \"/etc/rc.d/init.d/jabber-asa-transport start\" to start Jabber ASA transport."
fi

%preun
if [ "$1" = "0" ]; then
	if [ -r /var/lock/subsys/jabber-asa-transport ]; then
		/etc/rc.d/init.d/jabber-asa-transport stop >&2
	fi
	/sbin/chkconfig --del jabber-asa-transport
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog AUTHORS README
%attr(755,root,root) %{_sbindir}/*
%attr(640,root,jabber) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/jabber/asa.xml
%attr(754,root,root) /etc/rc.d/init.d/jabber-asa-transport
%attr(770,root,jabber) /var/lib/jabber/asa
%attr(755,root,root) %{_libdir}/jabber/asa/plugins/*
