
%global			_hardened_build 1

%if 0%{?fedora} >= 15 || 0%{?rhel} >= 7
%global with_nfsidmap 1
%else
%global with_nfsidmap 0
%endif

%if ( 0%{?fedora} >= 18 || 0%{?rhel} >= 7 )
%global with_systemd 1
%else
%global with_systemd 0
%endif

# Conditionally enable some FSALs, disable others.
#
# 1. rpmbuild accepts these options (gpfs as example):
#    --with gpfs
#    --without gpfs

%define on_off_switch() %%{?with_%1:ON}%%{!?with_%1:OFF}

# A few explanation about %%bcond_with and %%bcond_without
# /!\ be careful: this syntax can be quite messy
# %%bcond_with means you add a "--with" option, default = without this feature
# %%bcond_without adds a"--without" so the feature is enabled by default

#%%bcond_without gpfs
%global use_fsal_gpfs OFF

%if 0%{?fedora} || 0%{?rhel} > 6
%bcond_without xfs
%else
%bcond_with xfs
%endif
%global use_fsal_xfs %{on_off_switch xfs}

%bcond_without ceph
%global use_fsal_ceph %{on_off_switch ceph}

#%%bcond_with lustre
%global use_fsal_lustre OFF

#%%bcond_with shook
%global use_fsal_shook OFF

%if 0%{?fedora} || 0%{?rhel} > 6
%bcond_without gluster
%else
%bcond_with gluster
%endif
%global use_fsal_gluster %{on_off_switch gluster}

#%%bcond_with hpss
%global use_fsal_hpss OFF

#%%bcond_without panfs
%global use_fsal_panfs OFF

#%%bcond_with pt
%global use_fsal_pt OFF

%bcond_with rdma
%global use_rdma %{on_off_switch rdma}

%bcond_without jemalloc

#%%bcond_with lustre_up
%global use_lustre_up OFF

#%%bcond_with lttng
%global use_lttng OFF

%bcond_without utils
%global use_utils %{on_off_switch utils}

%bcond_without gui_utils
%global use_gui_utils %{on_off_switch gui_utils}

#%%global dev_version %{lua: extraver = string.gsub('-rc-final', '%-', ''); print(extraver) }

%global		ntirpcname	ntirpc
%global		ntirpcvers	1.2.1
%global		versiontag	2.2.0

Name:		nfs-ganesha
Version:	2.2.0
Release:	2%{?dev_version:%{dev_version}}%{?dist}
Summary:	NFS-Ganesha is a NFS Server running in user space
Group:		Applications/System
License:	LGPLv3+
Url:		https://github.com/nfs-ganesha/nfs-ganesha/wiki

Source0:	https://github.com/%{name}/%{name}/archive/V%{versiontag}/%{name}-%{version}.tar.gz
Source1:	https://github.com/%{name}/%{ntirpcname}/archive/v%{ntirpcvers}/%{ntirpcname}-%{ntirpcvers}.tar.gz

# Bundling exception through Fedora 23
# https://fedorahosted.org/fpc/ticket/363
Provides:	bundled(libntirpc)

BuildRequires:	cmake
BuildRequires:	bison flex
BuildRequires:	flex
BuildRequires:	pkgconfig
BuildRequires:	krb5-devel
BuildRequires:	dbus-devel
BuildRequires:	libcap-devel
BuildRequires:	libblkid-devel
BuildRequires:	libuuid-devel
Requires:	dbus
Requires:	nfs-utils
%if %{with_nfsidmap}
BuildRequires:	libnfsidmap-devel
%else
BuildRequires:	nfs-utils-lib-devel
%endif
%if %{with rdma}
BuildRequires:	libmooshika-devel >= 0.6-0
%endif
%if %{with jemalloc}
BuildRequires:	jemalloc-devel
%endif
%if %{with lustre_up}
BuildRequires:	lcap-devel >= 0.1-0
%endif
%if %{with_systemd}
BuildRequires:	systemd
Requires(post):	systemd
Requires(preun): systemd
Requires(postun): systemd
%else
BuildRequires:	initscripts
%endif

# Use CMake variables

%description
nfs-ganesha : NFS-GANESHA is a NFS Server running in user space.
It comes with various back-end modules (called FSALs) provided as
 shared objects to support different file systems and name-spaces.

%package mount-9P
Summary: a 9p mount helper
Group: Applications/System
Requires: nfs-ganesha = %{version}-%{release}

%description mount-9P
This package contains the mount.9P script that clients can use
to simplify mounting to NFS-GANESHA. This is a 9p mount helper.

%package vfs
Summary: The NFS-GANESHA's VFS FSAL
Group: Applications/System
BuildRequires: libattr-devel
Requires: nfs-ganesha = %{version}-%{release}

%description vfs
This package contains a FSAL shared object to
be used with NFS-Ganesha to support VFS based filesystems

%package nullfs
Summary: The NFS-GANESHA's NULLFS Stackable FSAL
Group: Applications/System
Requires: nfs-ganesha = %{version}-%{release}

%description nullfs
This package contains a Stackable FSAL shared object to
be used with NFS-Ganesha. This is mostly a template for future (more sophisticated) stackable FSALs

%package proxy
Summary: The NFS-GANESHA's PROXY FSAL
Group: Applications/System
BuildRequires: libattr-devel
Requires: nfs-ganesha = %{version}-%{release}

%description proxy
This package contains a FSAL shared object to
be used with NFS-Ganesha to support PROXY based filesystems

%if %{with utils}
%package utils
Summary: The NFS-GANESHA's util scripts
Group: Applications/System
%if %{with gui_utils}
BuildRequires:	PyQt4-devel
Requires:	PyQt4
%endif
Requires: nfs-ganesha = %{version}-%{release}, python

%description utils
This package contains utility scripts for managing the NFS-GANESHA server
%endif

%if %{with lttng}
%package lttng
Summary: The NFS-GANESHA's library for use with LTTng
Group: Applications/System
BuildRequires: lttng-ust-devel >= 2.3
Requires: nfs-ganesha = %{version}-%{release}, lttng-tools >= 2.3,  lttng-ust >= 2.3

%description lttng
This package contains the libganesha_trace.so library. When preloaded
to the ganesha.nfsd server, it makes it possible to trace using LTTng.
%endif

# Option packages start here. use "rpmbuild --with lustre" (or equivalent)
# for activating this part of the spec file

# GPFS
%if %{with gpfs}
%package gpfs
Summary: The NFS-GANESHA's GPFS FSAL
Group: Applications/System
Requires: nfs-ganesha = %{version}-%{release}

%description gpfs
This package contains a FSAL shared object to
be used with NFS-Ganesha to support GPFS backend
%endif

# CEPH
%if %{with ceph}
%package ceph
Summary: The NFS-GANESHA's CEPH FSAL
Group: Applications/System
Requires:	ceph >= 0.78
BuildRequires:	ceph-devel >= 0.78
Requires: nfs-ganesha = %{version}-%{release}

%description ceph
This package contains a FSAL shared object to
be used with NFS-Ganesha to support CEPH
%endif

# LUSTRE
%if %{with lustre}
%package lustre
Summary: The NFS-GANESHA's LUSTRE FSAL
Group: Applications/System
Requires: nfs-ganesha = %{version}-%{release}, lustre
BuildRequires:	libattr-devel lustre

%description lustre
This package contains a FSAL shared object to
be used with NFS-Ganesha to support LUSTRE
%endif

# SHOOK
%if %{with shook}
%package shook
Summary: The NFS-GANESHA's LUSTRE/SHOOK FSAL
Group: Applications/System
Requires: nfs-ganesha = %{version}-%{release}, lustre, shook-client
BuildRequires:	libattr-devel lustre shook-devel

%description shook
This package contains a FSAL shared object to
be used with NFS-Ganesha to support LUSTRE via SHOOK
%endif

# XFS
%if %{with xfs}
%package xfs
Summary: The NFS-GANESHA's XFS FSAL
Group: Applications/System
Requires: nfs-ganesha = %{version}-%{release}
BuildRequires:	libattr-devel xfsprogs-devel

%description xfs
This package contains a shared object to be used with FSAL_VFS
to support XFS correctly
%endif

# HPSS
%if %{with hpss}
%package hpss
Summary: The NFS-GANESHA's HPSS FSAL
Group: Applications/System
Requires: nfs-ganesha = %{version}-%{release}
#BuildRequires:	hpssfs

%description hpss
This package contains a FSAL shared object to
be used with NFS-Ganesha to support HPSS
%endif

# PANFS
%if %{with panfs}
%package panfs
Summary: The NFS-GANESHA's PANFS FSAL
Group: Applications/System
Requires: nfs-ganesha = %{version}-%{release}

%description panfs
This package contains a FSAL shared object to
be used with NFS-Ganesha to support PANFS
%endif

# PT
%if %{with pt}
%package pt
Summary: The NFS-GANESHA's PT FSAL
Group: Applications/System
Requires: nfs-ganesha = %{version}-%{release}

%description pt
This package contains a FSAL shared object to
be used with NFS-Ganesha to support PT
%endif

# GLUSTER
%if %{with gluster}
%package gluster
Summary: The NFS-GANESHA's GLUSTER FSAL
Group: Applications/System
Requires: nfs-ganesha = %{version}-%{release}
BuildRequires:	glusterfs-api-devel >= 3.5.1
BuildRequires:	libattr-devel

%description gluster
This package contains a FSAL shared object to
be used with NFS-Ganesha to support Gluster
%endif

%prep
%setup -q -n %{name}-%{versiontag} -a 1
rm -rf contrib/libzfswrapper
mv %{ntirpcname}-%{ntirpcvers}/* src/libntirpc/

%build
%cmake ./src -DCMAKE_BUILD_TYPE=Debug			\
	-DBUILD_CONFIG=rpmbuild				\
	-DUSE_FSAL_ZFS=NO				\
	-DUSE_FSAL_XFS=%{use_fsal_xfs}			\
	-DUSE_FSAL_CEPH=%{use_fsal_ceph}		\
	-DUSE_FSAL_LUSTRE=%{use_fsal_lustre}		\
	-DUSE_FSAL_SHOOK=%{use_fsal_shook}		\
	-DUSE_FSAL_GPFS=%{use_fsal_gpfs}		\
	-DUSE_FSAL_HPSS=%{use_fsal_hpss}		\
	-DUSE_FSAL_PANFS=%{use_fsal_panfs}		\
	-DUSE_FSAL_PT=%{use_fsal_pt}			\
	-DUSE_FSAL_GLUSTER=%{use_fsal_gluster}		\
	-DUSE_9P_RDMA=%{use_rdma}			\
	-DUSE_FSAL_LUSTRE_UP=%{use_lustre_up}		\
	-DUSE_LTTNG=%{use_lttng}			\
	-DUSE_ADMIN_TOOLS=%{use_utils}			\
	-DUSE_GUI_ADMIN_TOOLS=%{use_gui_utils}		\
	-DUSE_FSAL_VFS=ON				\
	-DUSE_FSAL_PROXY=ON				\
	-DUSE_DBUS=ON					\
	-DUSE_9P=ON					\
	-DDISTNAME_HAS_GIT_DATA=OFF			\
	-DCMAKE_INSTALL_PREFIX=				\
%if %{with jemalloc}
	-DALLOCATOR=jemalloc
%endif

make %{?_smp_mflags} || make %{?_smp_mflags} || make

%install
mkdir -p %{buildroot}%{_sysconfdir}/ganesha/
mkdir -p %{buildroot}%{_sysconfdir}/dbus-1/system.d
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_libdir}/ganesha
mkdir -p %{buildroot}%{_localstatedir}/run/ganesha
install -m 644 src/config_samples/logrotate_ganesha	%{buildroot}%{_sysconfdir}/logrotate.d/ganesha
install -m 644 src/scripts/ganeshactl/org.ganesha.nfsd.conf	%{buildroot}%{_sysconfdir}/dbus-1/system.d
install -m 755 src/tools/mount.9P	%{buildroot}%{_sbindir}/mount.9P

install -m 644 src/config_samples/vfs.conf %{buildroot}%{_sysconfdir}/ganesha

%if %{with_systemd}
mkdir -p %{buildroot}%{_unitdir}
install -m 644 src/scripts/systemd/nfs-ganesha.service	%{buildroot}%{_unitdir}/nfs-ganesha.service
install -m 644 src/scripts/systemd/nfs-ganesha-lock.service	%{buildroot}%{_unitdir}/nfs-ganesha-lock.service
install -m 644 src/scripts/systemd/sysconfig/nfs-ganesha	%{buildroot}%{_sysconfdir}/sysconfig/ganesha
%else
mkdir -p %{buildroot}%{_sysconfdir}/init.d
install -m 755 src/scripts/init.d/nfs-ganesha		%{buildroot}%{_sysconfdir}/init.d/nfs-ganesha
install -m 644 src/scripts/init.d/sysconfig/ganesha		%{buildroot}%{_sysconfdir}/sysconfig/ganesha
%endif

%if %{with utils} && 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%if %{with pt}
install -m 755 src/ganesha.pt.init %{buildroot}%{_sysconfdir}/init.d/nfs-ganesha-pt
install -m 644 src/config_samples/pt.conf %{buildroot}%{_sysconfdir}/ganesha
%endif

%if %{with xfs}
install -m 644 src/config_samples/xfs.conf %{buildroot}%{_sysconfdir}/ganesha
%endif

%if %{with ceph}
install -m 644 src/config_samples/ceph.conf %{buildroot}%{_sysconfdir}/ganesha
%endif

%if %{with lustre}
install -m 755 src/config_samples/lustre.conf %{buildroot}%{_sysconfdir}/ganesha
%endif

%if %{with gpfs}
install -m 644 src/config_samples/gpfs.conf	%{buildroot}%{_sysconfdir}/ganesha
install -m 644 src/config_samples/gpfs.ganesha.nfsd.conf %{buildroot}%{_sysconfdir}/ganesha
install -m 644 src/config_samples/gpfs.ganesha.main.conf %{buildroot}%{_sysconfdir}/ganesha
install -m 644 src/config_samples/gpfs.ganesha.log.conf %{buildroot}%{_sysconfdir}/ganesha
install -m 644 src/config_samples/gpfs.ganesha.exports.conf	%{buildroot}%{_sysconfdir}/ganesha
%endif

%if %{with utils}
pushd .
cd scripts/ganeshactl/
python setup.py --quiet install --root=%{buildroot}
popd
install -m 755 Protocols/NLM/sm_notify.ganesha		%{buildroot}%{_bindir}/sm_notify.ganesha
%endif

make DESTDIR=%{buildroot}/usr install
rm -f %{buildroot}/usr/bin/libntirpc.a
mv %{buildroot}/usr%{_sysconfdir}/ganesha/ganesha.conf %{buildroot}%{_sysconfdir}/ganesha/

%post
%if %{with_systemd}
%systemd_post nfs-ganesha.service
%systemd_post nfs-ganesha-lock.service
%endif

%preun
%if %{with_systemd}
%systemd_preun nfs-ganesha-lock.service
%endif

%postun
%if %{with_systemd}
%systemd_postun_with_restart nfs-ganesha-lock.service
%endif

%files
%{!?_licensedir:%global license %%doc}
%license src/LICENSE.txt
%defattr(-,root,root,-)
%{_bindir}/ganesha.nfsd
#%%{_bindir}/libntirpc.a
%config %{_sysconfdir}/dbus-1/system.d/org.ganesha.nfsd.conf
%config(noreplace) %{_sysconfdir}/sysconfig/ganesha
%config(noreplace) %{_sysconfdir}/logrotate.d/ganesha
%dir %{_sysconfdir}/ganesha/
%config(noreplace) %{_sysconfdir}/ganesha/ganesha.conf
%dir %{_defaultdocdir}/ganesha/
%{_defaultdocdir}/ganesha/*
%dir %{_localstatedir}/run/ganesha

%if %{with_systemd}
%{_unitdir}/nfs-ganesha.service
%{_unitdir}/nfs-ganesha-lock.service
%else
%{_sysconfdir}/init.d/nfs-ganesha
%endif

%files mount-9P
%defattr(-,root,root,-)
%{_sbindir}/mount.9P


%files vfs
%defattr(-,root,root,-)
%{_libdir}/ganesha/libfsalvfs*
%config(noreplace) %{_sysconfdir}/ganesha/vfs.conf


%files nullfs
%defattr(-,root,root,-)
%{_libdir}/ganesha/libfsalnull*


%files proxy
%defattr(-,root,root,-)
%{_libdir}/ganesha/libfsalproxy*

# Optional packages
%if %{with gpfs}
%files gpfs
%defattr(-,root,root,-)
%{_libdir}/ganesha/libfsalgpfs*
%config(noreplace) %{_sysconfdir}/ganesha/gpfs.conf
%config(noreplace) %{_sysconfdir}/ganesha/gpfs.ganesha.nfsd.conf
%config(noreplace) %{_sysconfdir}/ganesha/gpfs.ganesha.main.conf
%config(noreplace) %{_sysconfdir}/ganesha/gpfs.ganesha.log.conf
%config(noreplace) %{_sysconfdir}/ganesha/gpfs.ganesha.exports.conf
%endif

%if %{with xfs}
%files xfs
%defattr(-,root,root,-)
%{_libdir}/ganesha/libfsalxfs*
%config(noreplace) %{_sysconfdir}/ganesha/xfs.conf
%endif

%if %{with ceph}
%files ceph
%defattr(-,root,root,-)
%{_libdir}/ganesha/libfsalceph*
%config(noreplace) %{_sysconfdir}/ganesha/ceph.conf
%endif

%if %{with lustre}
%files lustre
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/ganesha/lustre.conf
%{_libdir}/ganesha/libfsallustre*
%endif

%if %{with shook}
%files shook
%defattr(-,root,root,-)
%{_libdir}/ganesha/libfsalshook*
%endif

%if %{with gluster}
%files gluster
%defattr(-,root,root,-)
%{_libdir}/ganesha/libfsalgluster*
%endif

%if %{with hpss}
%files hpss
%defattr(-,root,root,-)
%{_libdir}/ganesha/libfsalhpss*
%endif

%if %{with panfs}
%files panfs
%defattr(-,root,root,-)
%{_libdir}/ganesha/libfsalpanfs*
%endif

%if %{with pt}
%files pt
%defattr(-,root,root,-)
%{_libdir}/ganesha/libfsalpt*
%config(noreplace) %{_sysconfdir}/init.d/nfs-ganesha-pt
%config(noreplace) %{_sysconfdir}/ganesha/pt.conf
%endif

%if %{with lttng}
%files lttng
%defattr(-,root,root,-)
%{_libdir}/ganesha/libganesha_trace*
%endif

%if %{with utils}
%files utils
%defattr(-,root,root,-)
%{python2_sitelib}/Ganesha/*
%{python2_sitelib}/ganeshactl-*-info
%if %{with gui_utils}
%{_bindir}/ganesha-admin
%{_bindir}/manage_clients
%{_bindir}/manage_exports
%{_bindir}/manage_logger
%{_bindir}/ganeshactl
%endif
%{_bindir}/fake_recall
%{_bindir}/get_clientids
%{_bindir}/grace_period
%{_bindir}/purge_gids
%{_bindir}/ganesha_stats
%{_bindir}/sm_notify.ganesha
%{_bindir}/ganesha_mgr
%endif

%changelog
* Fri May 15 2015 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.2.0-2
- %%license

* Tue Apr 21 2015 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.2.0-1
- 2.2.0 GA

* Mon Apr 20 2015 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.2.0-0.12rc-final
- 2.2.0-0.12rc-final

* Mon Apr 13 2015 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.2.0-0.11rc8
- 2.2.0-0.11rc8

* Mon Apr 6 2015 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.2.0-0.10rc7
- 2.2.0-0.10rc7
* Mon Mar 30 2015 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.2.0-0.9rc6
- 2.2.0-0.9rc6

* Sun Mar 22 2015 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.2.0-0.8rc5
- 2.2.0-0.8rc5

* Tue Mar 17 2015 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.2.0-0.7rc4
- ntirpc-1.2.1.tar.gz

* Tue Mar 17 2015 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.2.0-0.6rc4
- updated ntirpc-1.2.0.tar.gz

* Sun Mar 15 2015 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.2.0-0.5rc4
- 2.2.0-0.5rc4

* Mon Feb 23 2015 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.2.0-0.4rc3
- 2.2.0-0.4rc3

* Mon Feb 16 2015 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.2.0-0.3rc2
- subpackage Requires: nfs-ganesha = %%{version}-%%{release}

* Mon Feb 16 2015 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.2.0-0.2rc2
- 2.2.0-0.2rc2

* Fri Feb 13 2015 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.2.0-0.1rc1
- 2.2.0-0.1rc1
- nfs-ganesha.spec based on upstream

* Thu Feb 12 2015 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.1.0-14
- Fedora 23/rawhide build fixes
- Ceph restored in EPEL

* Mon Jan 19 2015 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.1.0-13
- Ceph retired from EPEL 7

* Thu Nov 6 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.1.0-12
- rebuild after libnfsidmap symbol version revert

* Wed Oct 29 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.1.0-11
- PyQt -> PyQt4 typo

* Mon Oct 27 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.1.0-10
- use upstream init.d script

* Thu Oct 2 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.1.0-9
- restore exclusion of gluster gfapi on rhel

* Thu Oct 2 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.1.0-8
- install /etc/dbus-1/system.d/org.ganesha.nfsd.conf
- build and install admin tools

* Mon Sep 29 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.1.0-7
- install /etc/sysconfig/nfs-ganesha file

* Fri Aug 29 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com>
- Ceph FSAL typo, #1135437

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jul 24 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.1.0-5
- use upstream nfs-ganesha.service

* Fri Jul 11 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.1.0-4
- keep fsal .so files, implementation now uses them

* Tue Jul 1 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.1.0-3
- static libuid2grp

* Tue Jul 1 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.1.0-2
- add libuid2grp.so

* Mon Jun 30 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.1.0-1
- nfs-ganesha-2.1.0 GA

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.0-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Jun 2 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.0.0-9
- Ceph FSAL enabled with ceph-0.80

* Wed May 21 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.0.0-8
- getdents()->getdents64(), struct dirent -> struct dirent64

* Sat May 10 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com>
- and exclude libfsalceph

* Sat May 10 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com>
- exclude libfsalgluster correctly

* Fri May 9 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.0.0-7
- Ceph FSAL, in a subpackage, (but requires ceph >= 0.78)

* Mon Mar 31 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com>
- GlusterFS FSAL in a subpackage
- EPEL7 has jemalloc as of 2014-02-25

* Tue Jan 21 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com>
- sussed out github archive so as to allow correct Source0

* Fri Jan 17 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.0.0-6
- EPEL7 and xfsprogs

* Fri Jan 17 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.0.0-5
- EPEL7

* Mon Jan 6 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.0.0-4
- with glusterfs-api(-devel) >= 3.4.2

* Sat Jan 4 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.0.0-3
- with glusterfs-api

* Thu Jan 2 2014 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.0.0-2
- Build on RHEL6. Add sample init.d script

* Wed Dec 11 2013 Jim Lieb <lieb@sea-troll.net> - 2.0.0-1
- Update to V2.0.0 release

* Mon Nov 25 2013 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.0.0-0.2.rcfinal
- update to RC-final

* Fri Nov 22 2013 Kaleb S. KEITHLEY <kkeithle at redhat.com> 2.0.0-0.1.rc5
- Initial commit
