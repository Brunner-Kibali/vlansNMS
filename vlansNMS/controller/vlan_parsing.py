from flask_sqlalchemy import SQLAlchemy

from vlansNMS.models.Vlans import Vlan
from vlansNMS.controller.logging_handlers import create_logger


class VlanInfo:
    def __init__(self, connection):
        """
        :param connection: a netmiko ssh connection that will be
        used during the course of an object created by the class to
        run commands and receive output.
        """
        self.logger = create_logger('vlan_info')
        self.connection = connection
        self.show_vlan_brief_output = None
        self.vlans = None

    def __call__(self, *args, **kwargs):
        self.get_vlans_metadata()
        return self.vlans

    def parse_vlan_string_output(self):
        """
        The information we get from the router is in a string format.
        And although this is simple and easy for us to read, for python
        to properly understand the information, we need to store it in a
        python data type e.g dictionary, list, string etc.

        This function deals with the conversion of the vlan information
        received from the command 'show vlan brief' to a format easier
        to deal with in python

        :returns -> a list of dictionaries. Each item on the list represents a vlan
            and the dictionary inside the list item is metadata for the specific vlan.
            e.g [
                {'vlan_id': '1', 'vlan_name': 'default', 'vlan_state': 'active'},
                {'vlan_id': '2', 'vlan_name': 'management', 'vlan_state': 'active'}
            ]
        """
        self.logger.debug(self.show_vlan_brief_output)
        # we split the string by newlines and then remove the first three lines
        # which are strings we will not need for this specific action
        # also remove the last blank line in the output received
        vlan_list = self.show_vlan_brief_output.split("\n")[3:-2]

        # keep each vlan as a new list on the vlan_list
        for i, single_vlan in enumerate(vlan_list):
            vlan_list[i] = single_vlan.split()

        # change list of lists to list of dictionaries that would be
        # easier to read
        vlan_dicts = []
        for single_vlan in vlan_list:
            single_vlan_dict = {
                'vlan_id': int(single_vlan[0]),
                'vlan_name': single_vlan[1],
                'vlan_state': single_vlan[2],
            }
            vlan_dicts.append(single_vlan_dict)
        return vlan_dicts

    def get_vlans_metadata(self):
        """
        Gets all the information that is needed for a single vlan.
        """
        self.logger.debug(f"start sending 'show vlan brief'")
        self.show_vlan_brief_output = self.connection.send_command("show vlan brief")
        self.logger.debug("parsing 'show vlan brief' string to python datatypes")
        self.vlans = self.parse_vlan_string_output()
        self.logger.debug("fetching vlan description")
        self.add_vlan_description()

    def add_vlan_description(self):
        """
        This methods aims at getting the description for each individual vlan.
        The 'show vlan brief' command used in self.parse_vlan_string_output()
        does not give us the descriptions so we need to manually get the
        description of the vlans through other means.

        :return: None.
        """

        for index, vlan in enumerate(self.vlans):
            self.logger.debug(f"start running 'show interface vlan {vlan['vlan_id']}'")
            vlan_id = vlan['vlan_id']
            vlan_details = self.connection.send_command("show interface vlan {}".format(vlan_id))
            description = VlanInfo.get_description(vlan_details)
            self.vlans[index]['vlan_description'] = description
            self.logger.debug(f"successfully completed running 'show interface vlan {vlan['vlan_id']}'")

    @staticmethod
    def get_description(show_interface_vlan_output: str):
        """
        :param show_interface_vlan_output: A string. The result gotten from
        running "show interface vlan x"
        :return: the description parsed from the output. This will be an
        empty string if the description for the vlan interface in question
        is not set
        """

        # get third line of the output. This is where the description usually
        # is. If the third line does not start with "Description:", then we know
        # the interface description has not yet been set.
        third_line_str = show_interface_vlan_output.split("\n")[2].strip()
        third_line_list = third_line_str.split()

        if third_line_list[0] != "Description:":
            return ""

        third_line_list.pop(0)
        return " ".join(third_line_list)


def insert_vlan(db: SQLAlchemy, vlan_id: int, vlan_name: str, vlan_description: str):
    logger = create_logger('insert_vlan')
    logger.debug(f'attempting to insert vlan id={vlan_id} name={vlan_name} description={vlan_description} to database')
    vlan = Vlan(id=vlan_id, name=vlan_name, description=vlan_description)
    db.session.add(vlan)
    db.session.commit()
    logger.debug(f'insertion attempt successful of vlan id={vlan_id} name={vlan_name} description={vlan_description}')


def create_vlan(connection, vlan_id, vlan_name, vlan_description):
    logger = create_logger('create_vlan')
    logger.debug(f"attempting to create vlan id={vlan_id} name={vlan_name} description={vlan_description}")
    config_commands = [
        "vlan {}".format(vlan_id),
        "name {}".format(vlan_name),
        "do copy running-config startup-config",
        "exit",
        "interface vlan {}".format(vlan_id),
        "description {}".format(vlan_description),
        "do copy running-config startup-config",
        "exit"
    ]
    connection.send_config_set(config_commands)
    logger.debug(f"attempt to create vlan id={vlan_id} name={vlan_name} description={vlan_description} successful")
