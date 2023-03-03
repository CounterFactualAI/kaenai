#!/bin/bash
curl -sfL https://get.k3s.io | sed -e 's/k3s-ci-builds.s3.amazonaws.com/s3.dualstack.us-east-1.amazonaws.com\/k3s-ci-builds/g' | INSTALL_K3S_COMMIT='${k3s_git_commit}' K3S_TOKEN='${k3s_token}' K3S_URL='${k3s_manager_protocol}://${k3s_manager_private_ip}:${k3s_manager_port}' sh -s - --docker --node-label=worker='true'
#link to ipv6 docker registry
sudo bash -c 'cat <<EOF >>/etc/docker/daemon.json
{
 "registry-mirrors": [
  "https://registry.ipv6.docker.com"
 ]
}
EOF'

#GPU
if [ '${gpu}' -ne "0" ]; then
	sudo yum-config-manager --disable amzn2-graphics

	distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
		&& curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.repo | sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo

	sudo yum install -y nvidia-docker2

	# When running kubernetes with docker, edit the config file which is usually present at /etc/docker/daemon.json to set up nvidia-container-runtime as the default low-level runtime:
	sudo bash -c 'cat << EOF > /etc/docker/daemon.json
	{
			"default-runtime": "nvidia",
			"runtimes": {
					"nvidia": {
							"path": "/usr/bin/nvidia-container-runtime",
							"runtimeArgs": []
					}
			},
      "registry-mirrors": [
        "https://registry.ipv6.docker.com"
      ]      
	}
EOF'

fi

sudo systemctl restart docker
# sudo systemctl restart k3s.service
sudo systemctl restart k3s-agent.service