# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "hulk-box"

  config.vm.box_url = "http://smi-vagrant.s3-website-us-west-2.amazonaws.com/hulk.html"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # sync up a tmp folder for dataset sharing
  # NOTE that this folder needs to exist on your host	
  #config.vm.synced_folder "/tmp/datasets", "/tmp/datasets"


  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  config.vm.network "forwarded_port", guest: 9000, host: 9000

  # This makes the box available to the outside world
  config.vm.network "public_network"

  # This makes the box able to talk to the 10.0.2.x network, because
  # Virtualbox will assign a 10.0.2.x IP to the box if this is not set
  # and then the box can't see the SMI network.
  config.vm.provider "virtualbox" do |vb|
   vb.customize ["modifyvm", :id, "--natnet1", "192.168.88/24"]
  end
end
