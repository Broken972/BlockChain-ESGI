from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.network import Consul
from diagrams.generic.compute import Rack
from diagrams.oci.governance import Tagging
from diagrams.aws.security import IdentityAndAccessManagementIamLongTermSecurityCredential, IdentityAndAccessManagementIamDataEncryptionKey

with Diagram("Processus de sélection d'un noeud de validation", show=False):
    with Cluster("Noeuds"):
        with Cluster("Noeud 1"):
            service_node1 = Rack("Noeud 1")
            consul1 = Consul("Consul")
            service_node1 >> Edge(label="                           ") >> consul1
            validator_tag1 = Tagging("Vérification du tag")
            consul1 >> Edge(label="Obtentions des services du cluster") >> validator_tag1

        with Cluster("Noeud 2"):
            service_node2 = Rack("Noeud 2")
            consul2 = Consul("Consul")
            service_node2 >> Edge(label="                           ") >> consul2
            validator_tag2 = Tagging("Vérification du tag")
            consul2 >> Edge(label="Obtentions des services du cluster") >> validator_tag2

        with Cluster("Noeud 3"):
            service_node3 = Rack("Noeud 3")
            consul3 = Consul("Consul")
            service_node3 >> Edge(label="                           ") >> consul3
            validator_tag3 = Tagging("Vérification du tag")
            consul3 >> Edge(label="Obtentions des services du cluster") >> validator_tag3

    selected_service = Consul("Service trouvé")
    [validator_tag1, validator_tag2, validator_tag3] >> Edge(label="") >> selected_service
    
    generate_signed_message = IdentityAndAccessManagementIamLongTermSecurityCredential("Récupération d'un message signé sur le noeud distant\nappartenant au service de validation")
    check_public_key = IdentityAndAccessManagementIamDataEncryptionKey("Vérification de la présence\nde la clé publique\ncorrespondante au message")

    selected_service >> Edge(label=f"{' '*31}") >> generate_signed_message
    generate_signed_message >> Edge(label=f"{' '*31}") >> check_public_key
