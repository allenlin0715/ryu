%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Summary: Ryu the Network Operating System.
Name: ryu
Version: 0.2
Release: 1
License: Apache v2.0
Group: Applications/Accessories
BuildArch: noarch
Source: %{name}-%{version}-%{release}.tar.gz
#Patch0: 
Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-root
Requires: python-gevent >= 0.13, python-gflags, python-sphinx, python-simplejson, python-webob >= 1.0.8

%description
Ryu is an open-sourced network operating system licensed under Apache
License v2. The project URL is http://www.osrg.net/ryu/ . Ryu aims to
provide logically centralized control and well defined API that makes
it easy for cloud operators to implement network management
applications on top of the Ryu. Currently, Ryu supports OpenFlow
protocol to control the network devices.

%prep

%setup -q

#%patch0 -p0

%build
%{__python} setup.py build

%install
%{__rm} -rf %{buildroot}

%{__python} setup.py install --skip-build --root %{buildroot}
%{__mkdir} -p %{buildroot}/etc/ryu/
%{__mv} %{buildroot}/usr/etc/ryu/ryu.conf %{buildroot}/etc/ryu/ryu.conf


#%check

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root,-)
/usr/bin/ryu-manager
/usr/bin/ryu-client
%doc README.rst LICENSE doc/*
%docdir /usr/shar/doc/{name}-%{version}
%{python_sitelib}/ryu/
%{python_sitelib}/ryu*.egg-info/
%config /etc/ryu/ryu.conf

%changelog
* Thu May 31 2012 ryu-devel ML <ryu-devel@lists.sourcefourge.net>
- Initial Release.
