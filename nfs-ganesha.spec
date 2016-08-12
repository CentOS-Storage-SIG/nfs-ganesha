
%global _hardened_build 1

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

%bcond_without nullfs
%global use_fsal_null %{on_off_switch nullfs}

%bcond_with proxy
%global use_proxy %{on_off_switch proxy}

%bcond_with gpfs
%global use_fsal_gpfs %{on_off_switch gpfs}

%bcond_with xfs
%global use_fsal_xfs %{on_off_switch xfs}

%bcond_with ceph
%global use_fsal_ceph %{on_off_switch ceph}

%bcond_with lustre
%global use_fsal_lustre %{on_off_switch lustre}

%bcond_with shook
%global use_fsal_shook %{on_off_switch shook}

%bcond_without gluster
%global use_fsal_gluster %{on_off_switch gluster}

%bcond_with hpss
%global use_fsal_hpss %{on_off_switch hpss}

%bcond_with panfs
%global use_fsal_panfs %{on_off_switch panfs}

%bcond_with pt
%global use_fsal_pt %{on_off_switch pt}

%bcond_with rdma
%global use_rdma %{on_off_switch rdma}

%bcond_with jemalloc

%bcond_with lustre_up
%global use_lustre_up %{on_off_switch lustre_up}

%bcond_with lttng
%global use_lttng %{on_off_switch lttng}

%ifarch aarch64
# PyQt4 is not available for aarch64 (in c7) yet
%bcond_with utils
%else
%bcond_without utils
%endif
%global use_utils %{on_off_switch utils}

%bcond_without gui_utils
%global use_gui_utils %{on_off_switch gui_utils}

%bcond_without system_ntirpc
%global use_system_ntirpc %{on_off_switch system_ntirpc}

%global dev_version %{lua: extraver = string.gsub('', '%-', '.'); print(extraver) }

Name:		nfs-ganesha
Version:	2.3.3
Release:	1%{?dev_version:%{dev_version}}%{?dist}
Summary:	NFS-Ganesha is a NFS Server running in user space
Group:		Applications/System
License:	LGPLv3+
Url:		https://github.com/nfs-ganesha/nfs-ganesha/wiki

Source0:	 https://github.com/%{name}/%{name}/archive/V%{version}/%{name}-%{version}%{dev_version}.tar.gz
Patch9999:	9999-Use-__gf_free-instead-of-libc-free.patch

BuildRequires:	cmake
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	pkgconfig
BuildRequires:	krb5-devel
BuildRequires:	dbus-devel
BuildRequires:	libcap-devel
BuildRequires:	libblkid-devel
BuildRequires:	libuuid-devel
%if %{with system_ntirpc}
BuildRequires:	libntirpc-devel >= 1.3.1
%endif
Requires:	nfs-utils
Requires:	rpcbind
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
BuildRequires: lcap-devel >= 0.1-0
%endif
%if %{with_systemd}
BuildRequires: systemd
Requires(post): systemd
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

%if %{with proxy}
%package proxy
Summary: The NFS-GANESHA's PROXY FSAL
Group: Applications/System
BuildRequires: libattr-devel
Requires: nfs-ganesha = %{version}-%{release}

%description proxy
This package contains a FSAL shared object to
be used with NFS-Ganesha to support PROXY based filesystems
%endif

%if %{with utils}
%package utils
Summary: The NFS-GANESHA's util scripts
Group: Applications/System
Requires:	dbus-python, pygobject2
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

# NULL
%if %{with nullfs}
%package nullfs
Summary: The NFS-GANESHA's NULLFS Stackable FSAL
Group: Applications/System
Requires: nfs-ganesha = %{version}-%{release}

%description nullfs
This package contains a Stackable FSAL shared object to
be used with NFS-Ganesha. This is mostly a template for future (more sophisticated) stackable FSALs
%endif

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
Requires:	nfs-ganesha = %{version}-%{release}
Requires:	ceph >= 0.78
BuildRequires:	ceph-devel >= 0.78

%description ceph
This package contains a FSAL shared object to
be used with NFS-Ganesha to support CEPH
%endif

# LUSTRE
%if %{with lustre}
%package lustre
Summary: The NFS-GANESHA's LUSTRE FSAL
Group: Applications/System
Requires:	nfs-ganesha = %{version}-%{release}
Requires:	lustre
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
Requires:	nfs-ganesha = %{version}-%{release}
Requires:	lustre shook-client
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
Requires:	nfs-ganesha = %{version}-%{release}
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
Requires:	nfs-ganesha = %{version}-%{release}
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
Requires:	nfs-ganesha = %{version}-%{release}

%description panfs
This package contains a FSAL shared object to
be used with NFS-Ganesha to support PANFS
%endif

# PT
%if %{with pt}
%package pt
Summary: The NFS-GANESHA's PT FSAL
Group: Applications/System
Requires:	nfs-ganesha = %{version}-%{release}


%description pt
This package contains a FSAL shared object to
be used with NFS-Ganesha to support PT
%endif

# GLUSTER
%if %{with gluster}
%package gluster
Summary: The NFS-GANESHA's GLUSTER FSAL
Group: Applications/System
Requires:	nfs-ganesha = %{version}-%{release}
BuildRequires:        glusterfs-api-devel >= 3.7.4
BuildRequires:        libattr-devel, libacl-devel

%description gluster
This package contains a FSAL shared object to
be used with NFS-Ganesha to support Gluster
%endif

%prep
%setup -q -n %{name}-%{version}%{dev_version}
rm -rf contrib/libzfswrapper
%patch9999 -b.__gf_free -p1

%build
cd src && %cmake . -DCMAKE_BUILD_TYPE=Debug		\
	-DBUILD_CONFIG=rpmbuild				\
	-DUSE_FSAL_NULL=%{use_fsal_null}		\
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
	-DUSE_SYSTEM_NTIRPC=%{use_system_ntirpc}	\
	-DUSE_9P_RDMA=%{use_rdma}			\
	-DUSE_FSAL_LUSTRE_UP=%{use_lustre_up}		\
	-DUSE_LTTNG=%{use_lttng}			\
	-DUSE_ADMIN_TOOLS=%{use_utils}			\
	-DUSE_GUI_ADMIN_TOOLS=%{use_gui_utils}		\
	-DUSE_FSAL_VFS=ON				\
	-DUSE_FSAL_PROXY=%{use_proxy}			\
	-DUSE_DBUS=ON					\
	-DUSE_9P=ON					\
	-DDISTNAME_HAS_GIT_DATA=OFF			\
%if %{with jemalloc}
	-DALLOCATOR=jemalloc
%endif

make %{?_smp_mflags} || make %{?_smp_mflags} || make

%install
cd src
mkdir -p %{buildroot}%{_sysconfdir}/ganesha/
mkdir -p %{buildroot}%{_sysconfdir}/dbus-1/system.d
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_libdir}/ganesha
mkdir -p %{buildroot}%{_localstatedir}/run/ganesha
mkdir -p %{buildroot}%{_libexecdir}/ganesha
install -m 644 config_samples/logrotate_ganesha	%{buildroot}%{_sysconfdir}/logrotate.d/ganesha
install -m 644 scripts/ganeshactl/org.ganesha.nfsd.conf	%{buildroot}%{_sysconfdir}/dbus-1/system.d
install -m 755 scripts/nfs-ganesha-config.sh %{buildroot}%{_libexecdir}/ganesha
install -m 755 tools/mount.9P	%{buildroot}%{_sbindir}/mount.9P

install -m 644 config_samples/vfs.conf %{buildroot}%{_sysconfdir}/ganesha

%if %{with_systemd}
mkdir -p %{buildroot}%{_unitdir}
install -m 644 scripts/systemd/nfs-ganesha.service	%{buildroot}%{_unitdir}/nfs-ganesha.service
install -m 644 scripts/systemd/nfs-ganesha-lock.service	%{buildroot}%{_unitdir}/nfs-ganesha-lock.service
install -m 644 scripts/systemd/nfs-ganesha-config.service %{buildroot}%{_unitdir}/nfs-ganesha-config.service
install -m 644 scripts/systemd/sysconfig/nfs-ganesha	%{buildroot}%{_sysconfdir}/sysconfig/ganesha
%else
mkdir -p %{buildroot}%{_sysconfdir}/init.d
install -m 755 scripts/init.d/nfs-ganesha		%{buildroot}%{_sysconfdir}/init.d/nfs-ganesha
install -m 644 scripts/init.d/sysconfig/ganesha		%{buildroot}%{_sysconfdir}/sysconfig/ganesha
%endif

%if %{with utils} && 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%if %{with pt}
install -m 644 config_samples/pt.conf %{buildroot}%{_sysconfdir}/ganesha
%endif

%if %{with xfs}
install -m 644 config_samples/xfs.conf %{buildroot}%{_sysconfdir}/ganesha
%endif

%if %{with ceph}
install -m 644 config_samples/ceph.conf %{buildroot}%{_sysconfdir}/ganesha
%endif

%if %{with lustre}
install -m 755 config_samples/lustre.conf %{buildroot}%{_sysconfdir}/ganesha
%endif

%if %{with gpfs}
install -m 755 scripts/gpfs-epoch %{buildroot}%{_libexecdir}/ganesha
install -m 644 config_samples/gpfs.conf	%{buildroot}%{_sysconfdir}/ganesha
install -m 644 config_samples/gpfs.ganesha.nfsd.conf %{buildroot}%{_sysconfdir}/ganesha
install -m 644 config_samples/gpfs.ganesha.main.conf %{buildroot}%{_sysconfdir}/ganesha
install -m 644 config_samples/gpfs.ganesha.log.conf %{buildroot}%{_sysconfdir}/ganesha
install -m 644 config_samples/gpfs.ganesha.exports.conf	%{buildroot}%{_sysconfdir}/ganesha
%if ! %{with_systemd}
mkdir -p %{buildroot}%{_sysconfdir}/init.d
install -m 755 scripts/init.d/nfs-ganesha.gpfs		%{buildroot}%{_sysconfdir}/init.d/nfs-ganesha-gpfs
%endif
%endif

make DESTDIR=%{buildroot} install

install -m 644 ChangeLog	%{buildroot}%{_defaultdocdir}/ganesha

%post
%if %{with_systemd}
%systemd_post nfs-ganesha.service
%systemd_post nfs-ganesha-lock.service
%systemd_post nfs-ganesha-config.service
%endif
killall -SIGHUP dbus-daemon 2>&1 > /dev/null

%preun
%if %{with_systemd}
%systemd_preun nfs-ganesha-lock.service
%endif

%postun
%if %{with_systemd}
%systemd_postun_with_restart nfs-ganesha-lock.service
%endif

%files
%defattr(-,root,root,-)
%doc src/LICENSE.txt
%{_bindir}/ganesha.nfsd
%if ! %{with system_ntirpc}
%{_libdir}/libntirpc.so.1.3.0
%{_libdir}/libntirpc.so.1.3
%{_libdir}/libntirpc.so
%{_libdir}/pkgconfig/libntirpc.pc
%{_includedir}/ntirpc/
%endif
%config %{_sysconfdir}/dbus-1/system.d/org.ganesha.nfsd.conf
%config(noreplace) %{_sysconfdir}/sysconfig/ganesha
%config(noreplace) %{_sysconfdir}/logrotate.d/ganesha
%dir %{_sysconfdir}/ganesha/
%config(noreplace) %{_sysconfdir}/ganesha/ganesha.conf
%dir %{_defaultdocdir}/ganesha/
%doc %{_defaultdocdir}/ganesha/*
%dir %{_localstatedir}/run/ganesha
%dir %{_libexecdir}/ganesha
%{_libexecdir}/ganesha/nfs-ganesha-config.sh

%if %{with_systemd}
%{_unitdir}/nfs-ganesha.service
%{_unitdir}/nfs-ganesha-lock.service
%{_unitdir}/nfs-ganesha-config.service
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


%if %{with proxy}
%files proxy
%defattr(-,root,root,-)
%{_libdir}/ganesha/libfsalproxy*
%endif

# Optional packages
%if %{with nullfs}
%files nullfs
%defattr(-,root,root,-)
%{_libdir}/ganesha/libfsalnull*
%endif

%if %{with gpfs}
%files gpfs
%defattr(-,root,root,-)
%{_libdir}/ganesha/libfsalgpfs*
%config(noreplace) %{_sysconfdir}/ganesha/gpfs.conf
%config(noreplace) %{_sysconfdir}/ganesha/gpfs.ganesha.nfsd.conf
%config(noreplace) %{_sysconfdir}/ganesha/gpfs.ganesha.main.conf
%config(noreplace) %{_sysconfdir}/ganesha/gpfs.ganesha.log.conf
%config(noreplace) %{_sysconfdir}/ganesha/gpfs.ganesha.exports.conf
%{_libexecdir}/ganesha/gpfs-epoch
%if ! %{with_systemd}
%{_sysconfdir}/init.d/nfs-ganesha-gpfs
%endif
%endif

%if %{with xfs}
%files xfs
%{_libdir}/ganesha/libfsalxfs*
%config(noreplace) %{_sysconfdir}/ganesha/xfs.conf
%endif

%if %{with ceph}
%files ceph
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
%{_bindir}/client_stats_9pOps
%{_bindir}/export_stats_9pOps
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
* Fri Aug 12 2016 Niels de Vos <ndevos@redhat.com> 2.3.3-1
- Update to version 2.3.3

* Tue Aug 9 2016 Niels de Vos <ndevos@redhat.com> 2.3.2-3
- Prevent GF_CALLOC()/free() mismatch when upcalls are enabled
- Disable FSAL_PROXY

* Sat Jul 30 2016 Niels de Vos <ndevos@redhat.com> 2.3.2-2
- Disable FSAL_XFS for CentOS-6 build

* Wed Apr 27 2016 Niels de Vos <ndevos@redhat.com> 2.3.2-1
- Update to version 2.3.2
- do not package -utils on aarch64
- include the nfs-ganesha-config service for epoch generation

* Fri Oct 30 2015 Niels de Vos <ndevos@redhat.com> 2.3.0-1
- Import of nfs-ganesha from current Fedora Rawhide
- Disable the Ceph FSAL
- Disable usage of jemalloc
