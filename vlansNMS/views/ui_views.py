import os
from flask import redirect, url_for, request, render_template
from vlansNMS import app
from vlansNMS import db
from vlansNMS.controller.vlans import get_all_vlans
from vlansNMS.controller.insertion import update_entries
from vlansNMS.controller.deletions import delete_vlan_from_switch, delete_vlan_from_db
from vlansNMS.controller.vlan_parsing import VlanInfo, create_vlan, insert_vlan
from netmiko import ConnectHandler

connection_details = {
    "device_type": os.getenv("DEVICE_TYPE", "cisco_ios"),
    "host": os.getenv('DEVICE_ADDRESS'),
    "username": os.getenv('DEVICE_USERNAME'),
    "password": os.getenv('DEVICE_PASSWORD'),
    "port": os.getenv('DEVICE_PORT', '22')
}

connection = ConnectHandler(**connection_details)


@app.route('/')
def index():
    return 'Hello World!'


@app.route("/vlans/")
def all_vlans():
    vlans_in_db = get_all_vlans()
    context = {
        'all_vlans': vlans_in_db
    }
    return render_template('all_vlans.html', **context)


@app.route("/update-vlans")
def update_vlans():
    vlan_info = VlanInfo(connection)
    vlan_details = vlan_info()
    update_entries(vlan_details, db)
    return redirect(url_for('all_vlans'))


@app.route("/add-vlan", methods=['GET', 'POST'])
def add_vlan():
    if request.method == 'POST':
        result = request.form
        vlan_id = result.get('vlan_id')
        vlan_name = result.get('vlan_name')
        vlan_description = result.get('vlan_description')

        create_vlan(connection, vlan_id, vlan_name, vlan_description)

        insert_vlan(db, vlan_id, vlan_name, vlan_description)
        return redirect(url_for('all_vlans'))
    return render_template('add_vlan.html')


@app.route("/delete-vlan/<int:vlan_id>")
def delete_vlan(vlan_id):
    delete_vlan_from_switch(int(vlan_id), connection)
    delete_vlan_from_db(db, vlan_id)
    return redirect(url_for('all_vlans'))
