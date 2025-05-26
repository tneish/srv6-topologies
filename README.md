# srv6-topologies
SRv6 testing using containerlab and FRR

# Setup
I run all containers in a single VM, along with VSCode with the Containerlab extension and Wireshark.

The host is an Ubuntu Noble (24.04) VM with 8GB RAM, however most RAM goes to VSCode so you could do with less if you run headless.

The Xwin environment is minimal Openbox, which I use VNC to connect to.

The kernel needs the vrf module to setup VRFs.

Below is a quickstart, based on the following blogs:
- https://www.ducksource.blog/blog/primer-for-libvirt/
- https://bun.pages.forge.hefr.ch/docs/netsimulation/GNS3/FRR-Qemu

## Quickstart

Create disk image
```
$ sudo qemu-img create -f qcow2 /var/lib/libvirt/images/srv6-test.qcow2
```

Get Ubuntu image
```
$ wget https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img
```

Create cloud-init files to bootstrap the image. **Note!** Change user-credentials in the example below.

meta-data
```
instance-id: srv6-test
local-hostname: srv6-test
```

user-data
```
#cloud-config

users:
  - default
  - name: <<user>>
    sudo: "ALL=(ALL) NOPASSWD:ALL"
    groups: wheel,adm,systemd-journal,users,dialout,audio,netdev,video,plugdev,cdrom,games,input,gpio,spi,i2c,render,sudo,docker,messagebus
    #ssh_pwauth: True
    ssh_authorized_keys:
      - "<< insert pub key here, e.g. from ~/.ssh/id_ed25519.pub >>"
chpasswd:
  list: |
# change these below!
    root:<<rootpassword>>
    cloud-user:atomic
    <<user>>:<<password>>
  expire: False

ssh_pwauth: True

timezone: 'Europe/Stockholm'
hostname: srv6-test

# runs apt-get update
package_update: true

# runs apt-get upgrade
package_upgrade: true

packages:
  - apt-transport-https
  - ca-certificates
  - curl
  - gnupg-agent
  - software-properties-common
# for vrf module..
  - linux-image-generic

# Enable ipv4 forwarding, required on CIS hardened machines
write_files:
  - path: /etc/sysctl.d/90-ip-forwarding.conf
    content: |
      net.ipv4.conf.all.forwarding=1
      net.ipv6.conf.all.forwarding=1
      net.ipv6.conf.all.accept_ra=0
  - path: /etc/sysctl.d/95-srv6.conf
    content: |
      net.vrf.strict_mode = 1
      net.ipv4.conf.all.rp_filter = 0
      net.ipv6.seg6_flowlabel = 1
      net.ipv6.conf.all.seg6_enabled = 1
  - path: /etc/modules-load.d/modules.conf
    content: |
      vrf

# create the docker group
groups:
  - docker

# Install Docker, for production, consider pinning to stable versions
runcmd:
  - apt install xorg
  - apt install --no-install-recommends openbox
  - update alternatives set xwindow session manager openbox
  - curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
  - add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
  - apt-get update -y
  - apt-get install -y docker-ce docker-ce-cli containerd.io
  - systemctl daemon-reload
  - systemctl start docker
  - systemctl enable docker

# after system comes up first time.
final_message: "The system is finally up, after $UPTIME seconds"
```

burn to ISO
```
$ mkisofs -o cloudinit.iso -volid cidata -joliet -rock user-data meta-data
```
There is an easier way to inject the files, but this method should work.

Create the virtual machine.  Here using libvirt/virsh as a frontend to qemu/kvm but network testing is within the VM and there is no acceleration so almost anything will do.
```
$ virt-install --connect qemu:///system \
  --virt-type kvm \
  --name srv6-test \
  --ram 8192 \
  --vcpus=12 \
  --os-variant ubuntu24.04 \
  --graphics vnc \
  --disk /var/lib/libvirt/images/srv6-test.qcow2 \
  --cdrom /var/lib/libvirt/images/cloudinit.iso \
  --import \
  --network network=default,model=virtio
```

Once up and running you can connect using VNC and install vscode and containerlab extension. Then import a lab xml file.

If VNC doesn't come up you can connect to the VM via serial port, or SSH using the IP address allocated to the VM:

```
$ virsh net-dhcp-leases default
 Expiry Time           MAC address         Protocol   IP address           Hostname    Client ID or DUID
-------------------------------------------------------------------------------------------------------------------------------------------------
 2025-05-26 09:42:25   52:54:00:cf:bc:19   ipv4       192.168.122.224/24   srv6-test   ff:56:50:4d:98:00:02:00:00:ab:11:8b:e0:5a:5d:3a:d9:7e:25
```






