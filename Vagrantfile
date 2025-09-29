# Vagrantfile
Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-22.04"

  config.vm.define "db" do |db|
    db.vm.hostname = "db"
    db.vm.network "private_network", ip: "192.168.56.10"
    db.vm.provision "shell", path: "db/provision_db.sh"
  end

  config.vm.define "frontend" do |fe|
    fe.vm.hostname = "frontend"
    fe.vm.network "private_network", ip: "192.168.56.11"
    fe.vm.network "forwarded_port", guest: 5050, host: 5050, auto_correct: true
    fe.vm.provision "shell", path: "frontend/provision_frontend.sh"
  end

  config.vm.define "dashboard" do |dash|
    dash.vm.hostname = "dashboard"
    dash.vm.network "private_network", ip: "192.168.56.12"
    dash.vm.network "forwarded_port", guest: 6000, host: 6060, auto_correct: true
    dash.vm.provision "shell", path: "dashboard/provision_dashboard.sh"
  end

  config.vm.provider "virtualbox" do |vb|
    vb.memory = 1024
    vb.cpus = 2
  end
end
