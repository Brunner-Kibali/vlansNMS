from vlansNMS.controller.logging_handlers import create_logger
from vlansNMS.models.Vlans import Vlan


def delete_vlan_from_switch(vlan_id, connection):
    logger = create_logger('delete_vlan_from_switch')
    logger.debug(f'attempting to delete vlan {vlan_id} from switch')
    config_commands = [
        f'no vlan {vlan_id}',
        'copy running-config startup-config'
    ]
    connection.send_config_set(config_commands)
    logger.debug(f'successfully deleted vlan {vlan_id} from switch')


def delete_vlan_from_db(db, vlan_id):
    logger = create_logger('delete_vlan_from_db')
    logger.debug(f'attempting to delete vlan {vlan_id} from database')
    vlan = Vlan.query.get(vlan_id)
    db.session.delete(vlan)
    db.session.commit()
    logger.debug(f'successfully deleted vlan {vlan_id} from database')
