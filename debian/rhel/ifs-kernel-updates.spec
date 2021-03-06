%{!?kver: %global kver %(uname -r)}
%define kdir /lib/modules/%{kver}/build
%define kernel_version %{kver}

Name:           ifs-kernel-updates
Group:		System Environment/Kernel
Summary:        Extra kernel modules for IFS
Version:        %(echo %{kver}|sed -e 's/-/_/g')
Release:        724
License:        GPLv2
Source0:        %{name}-3.10.0_514.el7.x86_64.tgz
Source1:        %{name}.files
Source2:        %{name}.conf
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires:  %kernel_module_package_buildreqs

%define arch %(uname -p)
Requires:	kernel = %(echo %{kver} | sed -e 's/\(.*\)\.%{arch}/\1/g')

%kernel_module_package -f %{SOURCE1} default

# find our target version
%global kbuild %(
if [ -z "$kbuild" ]; then 
	echo "/lib/modules/%{kver}/build"
else 
	echo "$kbuild"
fi
)

%global kver %(
if [ -f "%{kbuild}/include/config/kernel.release" ]; then
	cat %{kbuild}/include/config/kernel.release
else
	echo "fail"
fi
)

%define modlist  rdmavt hfi1 ib_qib
%define kmod_moddir %kernel_module_package_moddir

%description
Updated kernel modules for OPA IFS

%package devel
Summary: Development headers for Intel HFI1 driver interface
Group: System Environment/Development

%description devel
Development header files for Intel HFI1 driver interface

%prep
%setup -qn %{name}-3.10.0_514.el7.x86_64
for flavor in %flavors_to_build; do
	for mod in %modlist; do
		rm -rf "$mod"_$flavor
		cp -r $mod  "$mod"_$flavor
	done
done

%build
if [ "%kver" = "fail" ]; then
        if [ -z "%kbuild" ]; then
                echo "The default target kernel, %kver, is not installed" >&2
                echo "To build, set \$kbuild to your target kernel build directory" >&2
        else
                echo "Cannot find kernel version in %kbuild" >&2
        fi
        exit 1
fi
echo "Kernel version is %kver"
echo "Kernel source directory is \"%kbuild\""
# Build
for flavor in %flavors_to_build; do
	for mod in %modlist; do
		rm -rf $mod
		cp -r "$mod"_$flavor $mod
		done
	echo rpm kernel_source %{kernel_source $flavor}
	make -j 8 CONFIG_INFINIBAND_RDMAVT=m KDIR=%{kernel_source $flavor} M=$PWD
	for mod in %modlist; do
		rm -rf "$mod"_$flavor
		mv -f $mod "$mod"_$flavor
        done
done

%install
install -m 644 -D %{SOURCE2} $RPM_BUILD_ROOT/etc/depmod.d/%{name}.conf
for flavor in %flavors_to_build ; do
	flv=$( [[ $flavor = default ]] || echo ".$flavor" )
	mkdir -p $RPM_BUILD_ROOT/lib/modules/%kver$flv/%kmod_moddir/%{name}
	for mod in %modlist; do
		if [[ "1" == "1" ]]; then
			RPM_KMOD_DIR=$RPM_BUILD_ROOT/../../KMODS
			if [ -d $RPM_KMOD_DIR ]; then
				install -m 644 -t $RPM_BUILD_ROOT/lib/modules/%kver$flv/%kmod_moddir/%{name} $RPM_KMOD_DIR/"$mod".ko
			else
				echo "WARNING: Installing unsigned kernel module: $mod.ko"
				install -m 644 -t $RPM_BUILD_ROOT/lib/modules/%kver$flv/%kmod_moddir/%{name} "$mod"_$flavor/"$mod".ko
			fi
		else
			install -m 644 -t $RPM_BUILD_ROOT/lib/modules/%kver$flv/%kmod_moddir/%{name} "$mod"_$flavor/"$mod".ko
		fi
	done
done
(targetdir=$RPM_BUILD_ROOT%{_includedir}/uapi/rdma/hfi/
 mkdir -p $targetdir
 srcdir=$(pwd)/include/rdma/hfi/
 cd %kdir
 sh ./scripts/headers_install.sh $targetdir $srcdir hfi1_user.h)

%files devel
%defattr(-,root,root,-)
%dir %{_includedir}/uapi/rdma
%dir %{_includedir}/uapi/rdma/hfi
%{_includedir}/uapi/rdma/hfi/hfi1_user.h

%changelog
* Wed Dec 21 2016 Alex Estrin <alex.estrin@intel.com>
- Add 'devel' package to supply exported header.
* Fri Sep 16 2016 Alex Estrin <alex.estrin@intel.com>
- Add KMP format spec. Minor fix for License string.
