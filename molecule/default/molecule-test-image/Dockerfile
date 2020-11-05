FROM centos:7

RUN yum -y install mailman openssh-server openssh-clients

RUN sed -i '/UsePAM/ s/yes/no/' /etc/ssh/sshd_config

RUN ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -N ''
RUN mkdir -m 700 /root/.ssh
COPY molecule_rsa.pub /root/.ssh/authorized_keys
RUN chmod 600 /root/.ssh/authorized_keys

CMD ["/usr/sbin/sshd", "-D"]
