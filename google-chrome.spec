%define		buildid	34537
%define		rel		1
Summary:	Google Chrome
Name:		google-chrome
Version:	4.0.249.43
Release:	%{buildid}.%{rel}
License:	Multiple, see http://chrome.google.com/
Group:		Applications/Networking
Source0:	http://dl.google.com/linux/rpm/stable/i386/%{name}-beta-%{version}-%{buildid}.i386.rpm
# Source0-md5:	e090d577a7b12181290dba715ec9f80b
Source1:	http://dl.google.com/linux/rpm/stable/x86_64/%{name}-beta-%{version}-%{buildid}.x86_64.rpm
# Source1-md5:	ae8d79ad89e6d9d9d1fcbc4d482badfd
Source2:	%{name}.sh
Source4:	find-lang.sh
Patch0:		chrome-desktop.patch
URL:		http://chrome.google.com/
BuildRequires:	rpm-utils
BuildRequires:	rpmbuild(macros) >= 1.453
BuildRequires:	sed >= 4.0
Requires:	browser-plugins >= 2.0
Requires:	nspr
Requires:	nss
Requires:	xdg-utils
Provides:	wwwbrowser
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		find_lang 	sh find-lang.sh %{buildroot}

%define		_enable_debug_packages	0
%define		no_install_post_strip	1

%define		nss_caps	libfreebl3.so libnss3.so libnssckbi.so libsmime3.so ibsoftokn3.so libssl3.so libnssutil3.so
%define		nspr_caps	libnspr4.so libplc4.so libplds4.so
%define		ffmpeg_caps	libffmpegsumo.so

# list of script capabilities (regexps) not to be used in Provides
%define		_noautoprov		%{nss_caps} %{nspr_caps} %{ffmpeg_caps}
# do not require them either
%define		_noautoreq		%{_noautoprov}

%description
The web browser from Google

Google Chrome is a browser that combines a minimal design with
sophisticated technology to make the web faster, safer, and easier.

%description -l hu.UTF-8
Webböngésző a Google-től.

Google Chrome egy böngésző, amely a minimalista külsőt házasítja össze
a kifinomult technológiával, hogy a webböngészés gyorsabb,
biztonságosabb és könnyebb legyen.

%prep
%setup -qcT
%ifarch %{ix86}
SOURCE=%{S:0}
%endif
%ifarch %{x8664}
SOURCE=%{S:1}
%endif

V=$(rpm -qp --qf '%{V}' $SOURCE)
R=$(rpm -qp --qf '%{R}' $SOURCE)
if [ version:$V != version:%{version} -o buildid:$R != buildid:%{buildid} ]; then
	exit 1
fi
rpm2cpio $SOURCE | cpio -i -d

mv opt/google/chrome .
mv usr/share/man/man1/* .
mv usr/share/gnome-control-center/default-apps .
mv chrome/default-app-block .
mv chrome/product_logo_*.{png,xpm} .
mv chrome/google-chrome.desktop .
mv chrome/google-chrome .
chmod a+x chrome/lib*.so*

# included in gnome-control-center-2.28.1-3
rm default-app-block default-apps/google-chrome.xml

%ifarch %{x8664}
# go figure, 32bit one doesn't have it compressed
gzip -d *.1.gz
%endif

%patch0 -p1

%{__sed} -e 's,@localedir@,%{_libdir}/%{name},' %{SOURCE4} > find-lang.sh
%{__sed} -i 's;/opt/google/chrome/product_logo_48.png;%{name}.png;' google-chrome.desktop
%{__sed} -i 's;/opt/google/chrome;%{_bindir};' google-chrome.desktop

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_libdir}/%{name}/plugins,%{_mandir}/man1,%{_pixmapsdir},%{_desktopdir},%{_libdir}/%{name}/themes}

install -p %{SOURCE2} $RPM_BUILD_ROOT%{_bindir}/%{name}
%{__sed} -i -e 's,@libdir@,%{_libdir}/%{name},' $RPM_BUILD_ROOT%{_bindir}/%{name}
cp -a chrome/* $RPM_BUILD_ROOT%{_libdir}/%{name}
cp -a google-chrome.1 $RPM_BUILD_ROOT%{_mandir}/man1
# for google-chrome --help
echo ".so google-chrome" > $RPM_BUILD_ROOT%{_mandir}/man1/chrome.1
cp -a product_logo_48.png $RPM_BUILD_ROOT%{_pixmapsdir}/%{name}.png
cp -a google-chrome.desktop $RPM_BUILD_ROOT%{_desktopdir}

%browser_plugins_add_browser %{name} -p %{_libdir}/%{name}/plugins

# nspr symlinks
for a in libnspr4.so libplc4.so libplds4.so; do
	ln -s %{_libdir}/$a $RPM_BUILD_ROOT%{_libdir}/%{name}/$a.0d
done
# nss symlinks
for a in libnss3.so libnssutil3.so libsmime3.so libssl3.so; do
	ln -s %{_libdir}/$a $RPM_BUILD_ROOT%{_libdir}/%{name}/$a.1d
done

# find locales
%find_lang %{name}.lang

%clean
rm -rf $RPM_BUILD_ROOT

%post
%update_browser_plugins

%postun
if [ "$1" = 0 ]; then
	%update_browser_plugins
fi

%files -f %{name}.lang
%defattr(644,root,root,755)

%{_browserpluginsconfdir}/browsers.d/%{name}.*
%config(noreplace) %verify(not md5 mtime size) %{_browserpluginsconfdir}/blacklist.d/%{name}.*.blacklist

%attr(755,root,root) %{_bindir}/%{name}
%{_mandir}/man1/*.1*
%{_pixmapsdir}/%{name}.png
%{_desktopdir}/*.desktop
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/chrome.pak
%dir %{_libdir}/%{name}/locales
%dir %{_libdir}/%{name}/plugins
%{_libdir}/%{name}/resources
%{_libdir}/%{name}/themes
%attr(755,root,root) %{_libdir}/%{name}/chrome
# These unique permissions are intentional and necessary for the sandboxing
%attr(4555,root,root) %{_libdir}/%{name}/chrome-sandbox

# ffmpeg libs
%attr(755,root,root) %{_libdir}/%{name}/libffmpegsumo.so

# nspr/nss symlinks
%attr(755,root,root) %{_libdir}/%{name}/libnspr4.so.0d
%attr(755,root,root) %{_libdir}/%{name}/libplc4.so.0d
%attr(755,root,root) %{_libdir}/%{name}/libplds4.so.0d
%attr(755,root,root) %{_libdir}/%{name}/libnss3.so.1d
%attr(755,root,root) %{_libdir}/%{name}/libnssutil3.so.1d
%attr(755,root,root) %{_libdir}/%{name}/libsmime3.so.1d
%attr(755,root,root) %{_libdir}/%{name}/libssl3.so.1d

# bundle this copy until xdg-utils will have this itself
%attr(755,root,root) %{_libdir}/%{name}/xdg-settings
