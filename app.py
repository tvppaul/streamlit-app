import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(layout="wide")

# 1. Initialize the Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Fetch Data from Individual Tabs
# (We clear the cache on sync to make sure we see updates instantly)
def load_data():
    models_df = conn.read(worksheet="product_models")
    inventory_df = conn.read(worksheet="inventory_units")
    customers_df = conn.read(worksheet="customers")
    integrations_df = conn.read(worksheet="integrations")
    tech_df = conn.read(worksheet="tech_logs")
    charge_df = conn.read(worksheet="charging_logs")
    return models_df, inventory_df, customers_df, integrations_df, tech_df, charge_df

models_df, inventory_df, customers_df, integrations_df, tech_df, charge_df = load_data()
voltages = ["24V", "48V", "76.8V", "80V", "108V"]
capacities = ["100A", "150A", "200A", "190AH", "201AH", "210AH", "280AH", "304AH", "340AH", "346AH", "380AH", "390AH", "410AH", "412AH", "420AH", "440AH", "460AH", "525AH", "560AH"]
@st.dialog("➕ Add a New Product Model")
def add_model_dialog():
    with st.form("add_model_form"):
        model_id = st.text_input("Model ID* (e.g., L48400)")
        category = st.selectbox("Category", ["Battery", "Charger", "Spare Part"])
        brand = st.text_input("Brand*")
        voltage = st.selectbox("Voltage", voltages)
        capacity = st.selectbox("Capacity", capacities)
        dimensions = st.text_input("Dimensions (e.g., 930-450-380)")
        weight = st.text_input("Weight (e.g., 220KG)")
        submitted = st.form_submit_button("💾 Save Model Blueprint")
        
        if submitted and model_id and brand:
            # Code to append to Google Sheets goes here...
            new_model = pd.DataFrame({
                "model_id": [model_id],
                "category": [category],
                "brand": [brand],
                "voltage": [voltage],
                "capacity": [capacity],
                "dimensions": [dimensions],
                "weight_kg": [weight],
            })
            updated_models_df = pd.concat([models_df, new_model], ignore_index=True)
            conn.update(worksheet="product_models", data=updated_models_df)
            st.success("New model added successfully! Refreshing app...")
            st.cache_data.clear()
            st.rerun()

@st.dialog("✏️ Edit Product Model")
def edit_model_dialog(model_id, category, brand, voltage, capacity, dimensions, weight, selected_idx):
    with st.form("edit_model_form"):
        model_id_edit = st.text_input("Model ID* (e.g., L48440)", value=str(model_id))
        # Locating the category index
        categories = ["Battery", "Charger", "Spare Part"]
        current_cat_idx = categories.index(category) if category in categories else 0
        category_edit = st.selectbox("Category", categories, index=current_cat_idx)
        brand_edit = st.text_input("Brand*", value=str(brand))

        # Locating the voltage index
        #voltages = ["24V", "48V", "76.8V", "80V", "108V"]
        current_volt_idx = voltages.index(voltage) if voltage in voltages else 0
        voltage_edit = st.selectbox("Voltage", voltages, index=current_volt_idx)
        
        # Locating the capacity index
        #capacities = ["100A", "200A", "190AH", "201AH", "340AH", "380AH", "390AH", "410AH", "412AH", "420AH", "440AH", "460AH", "525AH", "560AH"]
        current_cap_idx = capacities.index(capacity) if capacity in capacities else 0
        capacity_edit = st.selectbox("Capacity", capacities, index=current_cap_idx)

        dimensions_edit = st.text_input("Dimensions", value=str(dimensions))
        weight_edit = st.text_input("Weight (KG)", value=str(weight))
        submitted = st.form_submit_button("💾 Save Model Blueprint")
        
        if submitted and model_id_edit and brand_edit:
            updated_models_df = models_df.copy()
            updated_models_df.loc[selected_idx] = {
                "model_id": model_id_edit,
                "category": category_edit,
                "brand": brand_edit,
                "voltage": voltage_edit,
                "capacity": capacity_edit,
                "dimensions": dimensions_edit,
                "weight_kg": weight_edit,
            }
            conn.update(worksheet="product_models", data=updated_models_df)
            st.success("Product model updated! Refreshing app...")
            st.cache_data.clear()
            st.rerun()

@st.dialog("➕ Add Inventory Item")
def add_inventory():
    with st.form("add_inventory_form"):
        model_id = st.selectbox("Model ID*", models_df["model_id"])
        batch_date = st.date_input("Batch Date")
        serial_num = st.text_input("Serial Number*")
        status = st.selectbox("Status", ["In Stock", "Sold"])
        # Locating customer index
        cust_options = customers_df["customer_id"].tolist()
        cust_options.insert(0, "")
        customer_id = st.selectbox("Customer ID", cust_options)
        submitted = st.form_submit_button("💾 Save Item")
        
        if submitted and model_id and serial_num:
            new_item = pd.DataFrame({
                "model_id": [model_id],
                "batch_date": [batch_date.strftime("%d.%m.%y")],
                "serial_number": [serial_num],
                "status": [status],
                "customer_id": [customer_id]
            })
            updated_inventory_df = pd.concat([inventory_df, new_item], ignore_index=True)
            conn.update(worksheet="inventory_units", data=updated_inventory_df)
            st.success("Inventory item added successfully! Refreshing app...")
            st.cache_data.clear()
            st.rerun()

@st.dialog("✏️ Edit Inventory Item")
def edit_inventory(model_id, serial_number, batch_date, status, customer_id, selected_idx):
    with st.form("edit_inventory_form"):
        # Locating Model Id index
        models = models_df["model_id"].tolist()
        current_modelid_idx = models.index(model_id) if model_id in models else 0
        modelid_edit = st.selectbox("Model ID*", models, index=current_modelid_idx)

        # Modify date object
        default_date = (
            pd.to_datetime(batch_date).date()
            if pd.notna(batch_date) and str(batch_date).strip() != ""
            else pd.Timestamp.now().date()
        )
        batch_date_edit = st.date_input("Batch Date", value=default_date)

        serial_num_edit = st.text_input("Serial Number*", value=str(serial_number))

        # Locating status index
        statuses = ["In Stock", "Sold"]
        current_status_idx = statuses.index(status) if status in statuses else 0
        status_edit = st.selectbox("Status", statuses, index=current_status_idx)
        # Locating customer index
        cust_options = customers_df["customer_id"].tolist()
        cust_options.insert(0, "")
        current_cust_idx = cust_options.index(customer_id) if customer_id in cust_options else 0
        custid_edit = st.selectbox("Customer ID", cust_options, index=current_cust_idx)
        submitted = st.form_submit_button("💾 Save Item")
        
        if submitted and modelid_edit and serial_num_edit:
            updated_inventory_df = inventory_df.copy()
            updated_inventory_df.loc[selected_idx] = {
                "serial_number": serial_num_edit,
                "model_id": modelid_edit,
                "batch_date": batch_date_edit.strftime("%d.%m.%y"),
                "status": status_edit,
                "customer_id": custid_edit,
            }
            conn.update(worksheet="inventory_units", data=updated_inventory_df)
            st.success("Inventory item edited successfully! Refreshing app...")
            st.cache_data.clear()
            st.rerun()

def duplicate_inventory_item(model_id, batch_date, serial_num, status, customer_id):
    default_date = (
        pd.to_datetime(batch_date).date()
        if pd.notna(batch_date) and str(batch_date).strip() != ""
        else pd.Timestamp.now().date()
    )
    new_item = pd.DataFrame({
        "model_id": [model_id],
        "batch_date": [default_date.strftime("%d.%m.%y")],
        "serial_number": [serial_num],
        "status": [status],
        "customer_id": [customer_id]
    })
    updated_inventory_df = pd.concat([inventory_df, new_item], ignore_index=True)
    conn.update(worksheet="inventory_units", data=updated_inventory_df)
    st.success("Inventory item duplicated successfully! Refreshing app...")
    st.cache_data.clear()
    st.rerun()

def get_next_df_id(data_df: pd.DataFrame, id_col_str) -> int:
    """Calculates the next incremental ID based on the maximum existing integration_id."""
    # 1. Check if the dataframe is empty or missing the column
    if data_df.empty or id_col_str not in data_df.columns:
        return 1
    
    # 2. Drop NaN values and convert the column to numeric safely
    numeric_ids = pd.to_numeric(data_df[id_col_str], errors="coerce").dropna()
    
    # 3. If no valid numbers exist yet, start at 1
    if numeric_ids.empty:
        return 1
        
    # 4. Get the max ID and increment by 1
    return int(numeric_ids.max()) + 1

@st.dialog("➕ Add Customer & Forklift Info")
def add_cust_record(serial_number, inventory_idx):
    with st.form("add_cust_record_form"):
        integration_id = get_next_df_id(integrations_df, "integration_id")
        customer_id = st.text_input("Customer ID*")
        customer_name = st.text_input("Customer Name")
        location = st.text_input("Location")
        # Locating SN index
        sn_list = inventory_df["serial_number"].tolist()
        current_sn_idx = sn_list.index(serial_number) if serial_number in sn_list else 0
        sn = st.selectbox("Battery Serial Number*", sn_list, index=current_sn_idx)
        delivery_date = st.date_input("Delivery Date")
        # Forklift brands
        forklift_brands = ["Komatsu", "Toyota", "Nichiyu", "Mitsubishi", "Sumitomo", "TCM", "Unicarriers", "Nissan"]
        forklift_brand = st.selectbox("Forklift Brand", forklift_brands)
        forklift_model = st.text_input("Forklift Model")
        forklift_sn = st.text_input("Forklift S/N*")
        orig_battery_specs = st.text_input("Original Battery Specs")
        available_space = st.text_input("Available Space")
        required_weight = st.text_input("Required Weight")
        resulting_weight = st.text_input("Resulting Weight")
        empty_weight = st.text_input("Empty Weight")
        submitted = st.form_submit_button("💾 Save Record")

        if submitted and customer_id and sn and forklift_sn:
            new_customer = pd.DataFrame({
                "customer_id": [customer_id],
                "customer_name": [customer_name],
                "location": [location],
            })
            new_integration = pd.DataFrame({
                "integration_id": [integration_id],
                "customer_id": [customer_id],
                "serial_number": [sn],
                "delivery_date": [delivery_date.strftime("%d.%m.%y")],
                "forklift_brand": [forklift_brand],
                "forklift_model": [forklift_model],
                "forklift_sn": [forklift_sn],
                "orig_battery_specs": [orig_battery_specs],
                "available_space": [available_space],
                "required_weight": [required_weight],
                "resulting_weight": [resulting_weight],
                "empty_weight": [empty_weight],
            })
            updated_customers_df = pd.concat([customers_df, new_customer], ignore_index=True)
            updated_integrations_df = pd.concat([integrations_df, new_integration], ignore_index=True)
            assigned_cust_inventory = inventory_df.copy()
            assigned_cust_inventory.at[inventory_idx, "customer_id"] = customer_id
            assigned_cust_inventory.at[inventory_idx, "status"] = "Sold"
            conn.update(worksheet="customers", data=updated_customers_df)
            conn.update(worksheet="integrations", data=updated_integrations_df)
            conn.update(worksheet="inventory_units", data=assigned_cust_inventory)
            st.cache_data.clear()
            st.success("Customer & forklift record added successfully!")
            st.rerun()

@st.dialog("➕ Add Technical Log")
def add_tech_log(serial_number):
    with st.form("add_tech_log_form"):
        # Locating SN index
        tech_log_id = get_next_df_id(tech_df, "tech_log_id")
        sn_list = inventory_df["serial_number"].tolist()
        current_sn_idx = sn_list.index(serial_number) if serial_number in sn_list else 0
        sn = st.selectbox("Battery Serial Number*", sn_list, index=current_sn_idx)
        log_date = st.date_input("Log Date")
        log_types = ["Hardware", "Software"]
        log_type = st.selectbox("Log Type*", log_types)
        notes_txt = st.text_input("Notes*")
        submitted = st.form_submit_button("💾 Save Technical Log")
    if submitted and sn and log_type and notes_txt:
        timestamp = pd.Timestamp.now()
        new_log = pd.DataFrame({
            "tech_log_id": [tech_log_id],
            "serial_number": [sn],
            "log_date": [log_date.strftime("%d.%m.%y")],
            "timestamp": [timestamp.strftime("%H:%M:%S %d.%m.%y")],
            "log_type": [log_type],
            "notes": [notes_txt],
        })
        updated_tech_logs_df = pd.concat([tech_df, new_log], ignore_index=True)
        conn.update(worksheet="tech_logs", data=updated_tech_logs_df)
        st.cache_data.clear()
        st.success("A new tech log has been added successfully!")
        st.rerun()

@st.dialog("Add Charging Log")
def add_charge_log(serial_number):
    with st.form("add_charge_log_form"):
        # Locating SN index
        charge_log_id = get_next_df_id(charge_df, "charge_log_id")
        sn_list = inventory_df["serial_number"].tolist()
        current_sn_idx = sn_list.index(serial_number) if serial_number in sn_list else 0
        sn = st.selectbox("Battery Serial Number*", sn_list, index=current_sn_idx)
        charge_date = st.date_input("Charging Date*")
        started_time = st.text_input("Started Time")
        ended_time = st.text_input("Ended Time")
        initial_soc = st.slider("Initial %SOC*", 0, 100)
        final_soc = st.slider("Final %SOC*", 0, 100)
        initial_volt = st.text_input("Initial Voltage")
        final_volt = st.text_input("Final Voltage")
        charge_curr = st.text_input("Charging Current")
        charge_volt = st.text_input("Charging Voltage")
        primary_curr = st.text_input("Primary Current")
        notes_txt = st.text_input("Notes")
        submitted = st.form_submit_button("💾 Save Charging Log")
    if submitted and sn and initial_soc and final_soc:
        new_log = pd.DataFrame({
            "charge_log_id": [charge_log_id],
            "serial_number": [sn],
            "charging_date": [charge_date.strftime("%d.%m.%y")],
            "started_time": [started_time],
            "ended_time": [ended_time],
            "initial_soc": [initial_soc],
            "final_soc": [final_soc],
            "v_initial": [initial_volt],
            "v_final": [final_volt],
            "i_charging": [charge_curr],
            "v_charging": [charge_volt],
            "i_primary": [primary_curr],
            "notes": [notes_txt],
        })
        updated_charge_logs_df = pd.concat([charge_df, new_log], ignore_index=True)
        conn.update(worksheet="charging_logs", data=updated_charge_logs_df)
        st.cache_data.clear()
        st.success("A new charging log has been added successfully!")
        st.rerun()

def Product_Models():
    st.title("🔋 Lithium Battery Inventory Management")
    if models_df.empty:
        st.info("👋 Welcome! Your product models database is currently empty.")
        st.subheader("➕ Get Started: Add Your First Product Model")
        
        # Render the data entry form right here so they can fill up the sheet!
        with st.form("initial_model_form"):
            model_id = st.text_input("Model ID (e.g., L48400)")
            category = st.selectbox("Category", ["Battery", "Charger", "Spare Part"])
            brand = st.text_input("Brand")
            submitted = st.form_submit_button("Save Model Blueprint")
            
            if submitted and model_id and brand:
                # Code to append to Google Sheets goes here...
                new_model = pd.DataFrame({
                    "model_id": [model_id],
                    "category": [category],
                    "brand": [brand],
                })
                updated_models_df = pd.concat([models_df, new_model], ignore_index=True)
                conn.update(worksheet="product_models", data=updated_models_df)
                st.success("First model added successfully! Refreshing app...")
                st.cache_data.clear()
                st.rerun()
    else:
        ops_bar = st.container(horizontal=True)
        selected_row = st.dataframe(
            models_df, 
            on_select="rerun", 
            selection_mode="single-row",
            use_container_width=True
        )
        #Clear cache button for refreshing page
        if ops_bar.button("🧹 Clear Cache"):
            st.cache_data.clear()
            st.rerun()

        if ops_bar.button("➕ Add Model"):
            add_model_dialog()
        
        if selected_row["selection"]["rows"]:
            idx = selected_row["selection"]["rows"][0]
            model_id = models_df.iloc[idx]["model_id"]

            # Editable items
            category = models_df.iloc[idx]["category"]
            brand = models_df.iloc[idx]["brand"]
            voltage = models_df.iloc[idx]["voltage"]
            capacity = models_df.iloc[idx]["capacity"]
            dimensions = models_df.iloc[idx]["dimensions"]
            weight = models_df.iloc[idx]["weight_kg"]

            if ops_bar.button("✏️ Edit Model"):
                edit_model_dialog(model_id, category, brand, voltage, capacity, dimensions, weight, idx)

            if ops_bar.button("❌ Delete Model"):
                is_in_inventory = inventory_df["model_id"].astype(str).eq(str(model_id)).any()
                if not is_in_inventory:
                    updated_models_df = models_df.drop(index=idx)
                    conn.update(worksheet="product_models", data=updated_models_df)
                    st.cache_data.clear()
                    st.success("Product model deleted successfully!")
                    st.rerun()
                else:
                    st.error("Cannot delete this model. Please reassign or delete the related items in the inventory first.")
        

def Inventory():
    # ----------------- MAIN INVENTORY VIEW -----------------
    st.subheader("📦 Master Inventory")

    # Check if there is actually any inventory to show
    if inventory_df.empty:
        st.info("👋 Welcome! Your inventory database is currently empty.")
        st.subheader("➕ Get Started: Add Your First Item")
        
        # Render the data entry form right here so they can fill up the sheet!
        with st.form("initial_inventory_form"):
            model_id = st.selectbox("Model ID", models_df["model_id"])
            batch_date = st.date_input("Batch Date")
            serial_num = st.text_input("Serial Number")
            status = st.selectbox("Status", ["In Stock", "Sold"])
            submitted = st.form_submit_button("Save Item")
            
            if submitted and model_id and serial_num:
                # Code to append to Google Sheets goes here...
                new_item = pd.DataFrame({
                    "model_id": [model_id],
                    "batch_date": [batch_date.strftime("%d.%m.%y")],
                    "serial_number": [serial_num],
                    "status": [status],
                })
                updated_inventory_df = pd.concat([inventory_df, new_item], ignore_index=True)
                conn.update(worksheet="inventory_units", data=updated_inventory_df)
                st.success("First item added successfully! Refreshing app...")
                st.cache_data.clear()
                st.rerun()

    else:
        # ----------------- NORMAL RUNNING APP LOGIC -----------------
        # This runs only when the sheet has at least one row of data
        ops_bar = st.container(horizontal=True)
        # Merge function only gets model_id from inventory_df, data index the same as inventory_df
        merged_inventory = pd.merge(inventory_df, models_df, on="model_id", how="left")
        #Clear cache button for refreshing page
        if ops_bar.button("🧹 Clear Cache"):
            st.cache_data.clear()
            st.rerun()
            
        if ops_bar.button("➕ Add Item"):
            add_inventory()

        selected_row = st.dataframe(
            merged_inventory, 
            on_select="rerun", 
            selection_mode="single-row",
            use_container_width=True
        )

        # ----------------- DYNAMIC LOWER VIEW (No Tab Switching) -----------------
        if selected_row["selection"]["rows"]:
            idx = selected_row["selection"]["rows"][0]

            # Inventory editable items
            sn = merged_inventory.iloc[idx]["serial_number"]
            cust_id = merged_inventory.iloc[idx]["customer_id"]
            model_id = merged_inventory.iloc[idx]["model_id"]
            batch_date = merged_inventory.iloc[idx]["batch_date"]
            status = merged_inventory.iloc[idx]["status"]

            if ops_bar.button("✏️ Edit Item"):
                edit_inventory(model_id, sn, batch_date, status, cust_id, idx)

            if ops_bar.button("❌ Delete Item"):
                has_cust = customers_df["customer_id"].astype(str).eq(str(cust_id)).any()
                has_integrations = integrations_df["serial_number"].astype(str).eq(str(sn)).any()
                has_tech_logs = tech_df["serial_number"].astype(str).eq(str(sn)).any()
                has_charge_logs = charge_df["serial_number"].astype(str).eq(str(sn)).any()
                if not has_cust and not has_integrations and not has_tech_logs and not has_charge_logs:
                    updated_inventory_df = inventory_df.drop(index=idx)
                    conn.update(worksheet="inventory_units", data=updated_inventory_df)
                    st.cache_data.clear()
                    st.success("Inventory unit deleted successfully!")
                    st.rerun()
                else:
                    st.error("Cannot delete. Please remove the related info and/or logging first.")

            if ops_bar.button("📑 Duplicate Item"):
                duplicate_inventory_item(model_id, batch_date, sn, status, cust_id)

            st.markdown("---")
            st.subheader(f"🔍 Deep-Dive Timeline for Serial Number: :blue[{sn}]")
            
            # Create 3 localized sub-tabs for complete navigation without shifting pages
            tab1, tab2, tab3 = st.tabs(["Customer & Forklift Info", "Technical History", "Charging/Test Logs"])
            
            with tab1:
                tab1_bar = st.container(horizontal=True)
                if tab1_bar.button("➕ Add Record"):
                    add_cust_record(serial_number=sn, inventory_idx=idx)

                if pd.isna(cust_id) or cust_id == "":
                    st.info("Status: This unit is still in stock.")
                else:
                    # Relational Map: Filter and merge customer details with forklift configurations
                    client_info = customers_df[customers_df["customer_id"] == cust_id]
                    forklift_info = integrations_df[integrations_df["serial_number"] == sn]

                    # Merge function on customer_id but forklift_info not empty based on sn only
                    if not forklift_info.empty:
                        full_details = pd.merge(forklift_info, client_info, on="customer_id", how="left")
                        selected_row_tab1 = st.dataframe(
                            full_details, 
                            on_select="rerun", 
                            selection_mode="single-row",
                            use_container_width=True
                        )
                        if selected_row_tab1["selection"]["rows"]:
                            idx_tab1 = selected_row_tab1["selection"]["rows"][0]
                            target_cust_id = full_details.iloc[idx_tab1]["customer_id"]
                            target_sn = full_details.iloc[idx_tab1]["serial_number"]
                            # 1. Find customer_id index in customers_df and integrations_df
                            cust_matches = customers_df.index[customers_df["customer_id"] == target_cust_id].tolist()
                            real_cust_idx = cust_matches[0] if cust_matches else None
                            cust_matches_integ = integrations_df.index[integrations_df["customer_id"] == target_cust_id].tolist()
                            real_cust_idx_integ = cust_matches_integ[0] if cust_matches_integ else None

                            # 2. Find index in integrations_df
                            integ_matches = integrations_df.index[integrations_df["serial_number"] == target_sn].tolist()
                            real_integ_idx = integ_matches[0] if integ_matches else None

                            # Retrieve actual records from source DataFrames
                            #cust_record = customers_df.loc[real_cust_idx]
                            #integ_record = integrations_df.loc[real_integ_idx]
                            if tab1_bar.button("❌ Delete Record"):
                                updated_customers_df = customers_df.drop(index=real_cust_idx)
                                updated_integrations_df = integrations_df.drop(index=real_cust_idx_integ)
                                conn.update(worksheet="customers", data=updated_customers_df)
                                conn.update(worksheet="integrations", data=updated_integrations_df)
                                st.cache_data.clear()
                                st.success("Customer & forklift record deleted successfully!")
                                st.rerun()

                    else:
                        st.warning("Customer assigned but forklift conversion log is missing.")
                        
            with tab2:
                # Relational Filter: Instantly isolate hardware/software changes for this SN
                tab2_bar = st.container(horizontal=True)
                if tab2_bar.button("➕ Add Log"):
                    add_tech_log(serial_number=sn)

                unit_tech_logs = tech_df[tech_df["serial_number"] == sn]
                if not unit_tech_logs.empty:
                    st.dataframe(unit_tech_logs, use_container_width=True)
                else:
                    st.info("No software or hardware technical changes logged for this unit.")
                    
            with tab3:
                tab3_bar = st.container(horizontal=True)
                if tab3_bar.button("➕ Add Logging"):
                    add_charge_log(serial_number=sn)
                # Relational Filter: Pull only the charging telemetry logs for this unique asset
                unit_charge_logs = charge_df[charge_df["serial_number"] == sn]
                if not unit_charge_logs.empty:
                    st.dataframe(unit_charge_logs, use_container_width=True)
                else:
                    st.info("No battery charging tests recorded yet.")

pg = st.navigation([Product_Models, Inventory])
pg.run()