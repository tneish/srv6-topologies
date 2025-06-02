import os

def create_directories_and_files():
    """
    Creates 100 directories named 'isis-lowprioX' (where X is 1-100)
    in the current working directory, each containing a 'frr.conf' file.
    The 'frr.conf' file has placeholders replaced with the directory's suffix number.
    """
    frr_conf_template = """
frr version 10.3_git
frr defaults traditional
hostname isis-lowprio{suffix}
!
vrf vrf100
exit-vrf
!
interface eth0
 ipv6 router isis ipv6
 isis circuit-type level-2-only
 isis hello-interval 1
 isis hello-multiplier 3
exit
!
router isis ipv6
  net 49.0001.0001.01{suffix:02d}.00
#  lsp-mtu 1300
  topology ipv6-unicast
!
    """
    clab_conf_template = """
  nodes:
    isis-lowprio{suffix}:
      kind: linux
      image: quay.io/frrouting/frr:10.3.0
      binds: 
        - isis-lowprio{suffix}/daemons:/etc/frr/daemons
        - isis-lowprio{suffix}/frr.conf:/etc/frr/frr.conf
      exec:
        #        - ip link set eth0 down
        - ip link add vrf100 type vrf table 100
        - ip route add table 100 unreachable default metric 4278198272
        - ip link set dev vrf100 up
        - ip link set eth2 master vrf100
        - ip link set eth2 up
        - ip link set eth1 up
        - ip link set eth0 up

"""

    clab_file_path = "clab.add.conf"
    clab_f = open(clab_file_path, "w")
    j=1
    for i in range(1, 101):
        dir_name = f"isis-lowprio{i}"
        
        # Create the directory directly in the current working directory
        os.makedirs(dir_name, exist_ok=True)

        frr_conf_content = frr_conf_template.format(suffix=j)
        clab_conf_content = clab_conf_template.format(suffix=j)
        
        file_path = os.path.join(dir_name, "frr.conf")
        with open(file_path, "w") as f:
            f.write(frr_conf_content)

        clab_f.write(clab_conf_content)

        print(f"Created directory: {dir_name} and file: {file_path}")
        j+=1

    print(f"Wrote {clab_file_path}.")
   
if __name__ == "__main__":
    create_directories_and_files()
