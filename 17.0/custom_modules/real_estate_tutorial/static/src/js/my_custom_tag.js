/** @odoo-module **/

import { registry } from "@web/core/registry";

import { Component } from "@odoo/owl";

class MyCustomClientAction extends Component {}
MyCustomClientAction.template = "CustomActions"; //Este es el template definido en /xml/my_custom_Tag.xml

registry.category("actions").add("custom_client_action", MyCustomClientAction);