#!/bin/bash

# from https://github.wdf.sap.corp/AI/ml-api-facade/blob/sles-base-sp3/scripts/docker_install.sh
set -ex
# add local zypper repositories
rm -rf /usr/bin/container-suseconnect
rm -rf /usr/bin/container-suseconnect-zypp
zypper -n addrepo -g http://ls0110.wdf.sap.corp:1080/pub/mirrors/SUSE/Products/SLE-Module-Basesystem/15-SP3/x86_64/product/ SERVER
zypper -n addrepo -g http://ls0110.wdf.sap.corp:1080/pub/mirrors/SUSE/Updates/SLE-Module-Basesystem/15-SP3/x86_64/update/   UPDATE
zypper -n addrepo -g http://ls0110.wdf.sap.corp:1080/pub/mirrors/SUSE/Products/SLE-Module-Server-Applications/15-SP3/x86_64/product/   P_SERV
zypper -n addrepo -g http://ls0110.wdf.sap.corp:1080/pub/mirrors/SUSE/Updates/SLE-Module-Server-Applications/15-SP3/x86_64/update/   U_SERV
zypper -n addrepo -g http://ls0110.wdf.sap.corp:1080/pub/mirrors/SUSE/Products/SLE-Module-Development-Tools/15-SP3/x86_64/product/   P_DEV
zypper -n addrepo -g http://ls0110.wdf.sap.corp:1080/pub/mirrors/SUSE/Updates/SLE-Module-Development-Tools/15-SP3/x86_64/update/   U_DEV
zypper -n addrepo -g http://ls0110.wdf.sap.corp:1080/pub/mirrors/SUSE/Products/SLE-Module-Legacy/15-SP3/x86_64/product/   P_LEG
zypper -n addrepo -g http://ls0110.wdf.sap.corp:1080/pub/mirrors/SUSE/Updates/SLE-Module-Legacy/15-SP3/x86_64/update/   U_LEG
zypper -n addrepo -g http://ls0110.wdf.sap.corp:1080/pub/mirrors/SUSE/Products/SLE-Module-Public-Cloud/15-SP3/x86_64/product/   P_PC
zypper -n addrepo -g http://ls0110.wdf.sap.corp:1080/pub/mirrors/SUSE/Updates/SLE-Module-Public-Cloud/15-SP3/x86_64/update/   U_PC

zypper -n --gpg-auto-import-keys refresh

zypper --non-interactive addlock libdb-4_8  # do not install libdb-4_8 ever

echo "Force gpgchecks for all repos"
zypper --non-interactive modifyrepo --all --gpgcheck

echo "do not keep rpms"
zypper --non-interactive modifyrepo --all --keep-packages

ZYPPER_PACKAGES_GENERAL=(
 curl
 wget
)

ZYPPER_PACKAGES_PYTHON39=(
 python39
 python39-pip
)

if [ "$INSTALL_COMPILER" = true ] ; then
   ZYPPER_PACKAGES_COMPILER=(
     swig
     gcc7
     gcc7-c++
     gawk
     make
   )
else
   ZYPPER_PACKAGES_COMPILER=()
fi

ZYPPER_PACKAGES=(
 ${ZYPPER_PACKAGES_GENERAL[@]}
 ${ZYPPER_PACKAGES_MLF_TYOM[@]}
 ${ZYPPER_PACKAGES_COMPILER[@]}
 ${ZYPPER_PACKAGES_PYTHON39[@]}
)

ZYPPER_PACKAGES=${ZYPPER_PACKAGES[@]}
echo "install $ZYPPER_PACKAGES"

zypper --non-interactive update

zypper --non-interactive install --no-recommends --force-resolution ${ZYPPER_PACKAGES}

zypper --non-interactive clean -a

#echo "disable all zypper repos"
#zypper --non-interactive modifyrepo --disable --all


 # maintain symbolic link for gcc using gcc-7
 if [ "$INSTALL_COMPILER" = true ] ; then
     update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 10
     update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-7 10

     # required for installing certain python packages
     if [ ! -f /usr/bin/cc ] ; then
       ln -s /usr/bin/gcc /usr/bin/cc
     fi
 fi

update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 10
update-alternatives --install /usr/bin/python python /usr/bin/python3 10
update-alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.9 10
update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 10

  # some tests
python3.9 --version |& grep "Python 3.9"
python3 --version |& grep "Python 3.9"
pip3 --version |& grep "(python 3.9)"
pip --version |& grep "(python 3.9)"

 if [[ $(find / -name 'jinja.el') ]]; then
   exit 1
 fi

 # this does need to be part of the shipment
 rm $(basename "$0")
