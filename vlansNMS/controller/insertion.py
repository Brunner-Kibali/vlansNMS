from flask_sqlalchemy import SQLAlchemy
from vlansNMS.models.Vlans import Vlan
from vlansNMS.controller.logging_handlers import create_logger


def update_entries(incoming_entries: list, db: SQLAlchemy):
    logger = create_logger('update_entries')
    logger.debug("Vlan entries update requested")
    existing_vlan_ids = [
        vlan.id for vlan in db.session.query(Vlan).all()
    ]
    incoming_vlan_ids = []

    for entry in incoming_entries:
        incoming_vlan_ids.append(entry['vlan_id'])

        # if vlan already exists in db we update it.
        if entry['vlan_id'] in existing_vlan_ids:
            logger.debug(f"Vlan {entry['vlan_id']} found in db. Updating Vlan with most recent information")
            vlan = Vlan.query.get(entry['vlan_id'])
            vlan.name = entry['vlan_name']
            vlan.description = entry['vlan_description']
            vlan.state = entry['vlan_state']
            db.session.commit()
            logger.debug(f"Vlan {entry['vlan_id']} Update to db completed successfully.")

        # if vlan does not exist in db we insert it.
        else:
            logger.debug(f"Vlan {entry['vlan_id']} not found in db. Insertion beginning with data from switch")
            vlan = Vlan(
                id=entry['vlan_id'],
                name=entry['vlan_name'],
                description=entry['vlan_description'],
                state=entry['vlan_state']
            )
            db.session.add(vlan)
            db.session.commit()
            logger.debug(f"Vlan {entry['vlan_id']} insertion to db completed successfully")

    # check if the vlan has been removed from the switch configs
    for existing_id in existing_vlan_ids:
        if existing_id not in incoming_vlan_ids:

            logger.debug(f"Vlan {existing_id} found found in db but not on router. Deletion on db began")
            db.session.rollback()
            vlan = Vlan.query.get(existing_id)
            db.session.delete(vlan)
            db.session.commit()
            logger.debug(f"Vlan {existing_id} deletion from db completed successfully")

