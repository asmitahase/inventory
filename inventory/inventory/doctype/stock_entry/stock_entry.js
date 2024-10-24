// Copyright (c) 2024, Asmita Hase and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stock Entry", {
    refresh(frm){
        update_child_table(frm)
    },
	entry_type(frm) {
        update_child_table(frm)
	},

});

frappe.ui.form.on("Stock Entry Item",{
    item(frm,cdt,cdn){
        validate_stock(frm,cdt,cdn,'item')
        if (frm.doc.entry_type!="Receive") set_valuation_rate(cdt,cdn) 
    },
    source_warehouse(frm,cdt,cdn){
        validate_stock(frm,cdt,cdn,'source_warehouse')
        validate_warehouse(cdt,cdn,'source_warehouse')
        if (frm.doc.entry_type!="Receive") set_valuation_rate(cdt,cdn)
    },
    target_warehouse(frm,cdt,cdn){
        validate_warehouse(cdt,cdn,'target_warehouse')
    },
    quantity(frm,cdt,cdn){
        validate_quantity(frm,cdt,cdn)
    },
    rate(frm,cdt,cdn){
        validate_rate(cdt,cdn)
    }
})

function validate_rate(cdt,cdn){
    if (frappe.get_doc(cdt,cdn).rate <= 0){
        frappe.model.set_value(cdt, cdn, 'rate', undefined)
    }
}

function validate_quantity(frm,cdt,cdn){
    const quantity = frappe.get_doc(cdt,cdn).quantity
    if (quantity <= 0){
        frappe.model.set_value(cdt, cdn, 'quantity', undefined)
    }
    else{
        validate_stock(frm,cdt,cdn,'quantity')
    }
}

function validate_warehouse(cdt,cdn,field){
    const current_row = frappe.get_doc(cdt,cdn)
    if(
        current_row.source_warehouse && 
        current_row.target_warehouse && 
        current_row.source_warehouse == current_row.target_warehouse){
            frappe.throw("Source and Target warehouse cannot be the same")
            frappe.model.set_value(cdt, cdn, field, undefined)
        }
}
async function validate_stock(frm,cdt,cdn,field){
    const current_row = frappe.get_doc(cdt,cdn)
    if(current_row.item && current_row.source_warehouse && current_row.quantity){
        const available_item_stock = await get_item_stock(
            current_row.item,
            current_row.source_warehouse
        )
        const total_outgoing_quantity = get_total_outgoing_quantity(
            current_row.item,
            current_row.source_warehouse,
            frm.doc.items
        )
        console.log(total_outgoing_quantity)
        console.log(available_item_stock)
        if(total_outgoing_quantity > available_item_stock){
            frappe.msgprint({
                title:__(`Insufficient Stock of Item ${current_row.item}`),
                message:__(`Outgoing stock at ${current_row.source_warehouse} is less than is less than available stock.`),
                indicator:"red"
            })  
            frappe.model.set_value(cdt,cdn,field,undefined)  
        }
    } 
}
// get valuation rate for selected item from selected warehouse
async function get_item_stock(item,warehouse){
    return await frappe.call({
        method: "inventory.api.get_item_stock",
        args:{
            item:item,
            warehouse:warehouse
        },
}).then((res)=>res?.message)
}
async function set_valuation_rate(cdt,cdn){
    const current_row = frappe.get_doc(cdt,cdn)
    if (current_row.item && current_row.source_warehouse){
        let valuation_rate = await get_valuation_rate(current_row.item,current_row.source_warehouse)
        valuation_rate ? 
        frappe.model.set_value(cdt,cdn,'rate',valuation_rate) : 
        frappe.msgprint({
            title:__("No Item Stock"),
            message:__(`${current_row.item} is not in stock at ${current_row.source_warehouse}`),
            indicator:'red'
        })
    } 
}

async function get_valuation_rate(item,warehouse){
    return await frappe.call({
        method:"inventory.api.get_valuation_rate",
        args:{
            item:item,
            warehouse:warehouse
        }
    }).then((res)=>res?.message)
}

function get_total_outgoing_quantity(item,warehouse,all_items){
    let quantity = 0
    all_items.forEach(element => {
        if(element.item == item && element.source_warehouse == warehouse){
            quantity+=element.quantity
        }
    });
    return quantity
}

function update_child_table(frm){
    let entry_type = frm.doc.entry_type
    if ( entry_type == "Transfer"){
        frm.fields_dict.items.grid.toggle_reqd('source_warehouse',1)
        frm.fields_dict.items.grid.toggle_reqd('target_warehouse',1)
        frm.fields_dict.items.grid.toggle_enable('rate',0)
        frm.fields_dict.items.grid.toggle_enable('source_warehouse',1)
        frm.fields_dict.items.grid.toggle_enable('target_warehouse',1)
    }
    else if (entry_type == "Receive"){
        frm.fields_dict.items.grid.toggle_reqd('source_warehouse',0)
        frm.fields_dict.items.grid.toggle_reqd('target_warehouse',1)
        for (let row of frm.doc.items){
            frappe.model.set_value('Stock Entry Item',row.name,'source_warehouse',undefined)
        }
        frm.fields_dict.items.grid.toggle_enable('rate',1)
        frm.fields_dict.items.grid.toggle_enable('source_warehouse',0)
        frm.fields_dict.items.grid.toggle_enable('target_warehouse',1)
    }
    else if (entry_type == "Consume"){
        frm.fields_dict.items.grid.toggle_reqd('source_warehouse',1)
        frm.fields_dict.items.grid.toggle_reqd('target_warehouse',0)
        for (let row of frm.doc.items){
            frappe.model.set_value('Stock Entry Item',row.name,'target_warehouse',undefined)
        }
        frm.fields_dict.items.grid.toggle_enable('rate',0)
        frm.fields_dict.items.grid.toggle_enable('source_warehouse',1)
        frm.fields_dict.items.grid.toggle_enable('target_warehouse',0)
    }
}

// function make_fields_mandatory(frm){
//     // set the mandatory fields according to enrty type
//     const field_data_settings = {
//         'Receive': { 'source_warehouse': 0, 'target_warehouse': 1 },
//         'Transfer': { 'source_warehouse': 1, 'target_warehouse': 1 },
//         'Consume': {'source_warehouse': 1, 'target_warehouse': 0 }
//     }
//     console.log(Object.entries(mandatory_fields[frm.doc.entry_type]))
//     Object.entries(
//         mandatory_fields[frm.doc.entry_type]
//     ).forEach(
//         field => frm.fields_dict.items.grid.toggle_reqd(field[0],field[1])
//     )

// }