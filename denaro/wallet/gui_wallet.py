import tkinter as tk
from tkinter import ttk
import os
import sys
import pickledb
import subprocess
import traceback
from fastecdsa import keys, curve
from tkinter import simpledialog, messagebox

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path + "/../..")

from denaro.constants import CURVE
from denaro.helpers import point_to_string

class WalletApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.wallet_db = pickledb.load(f'{dir_path}/wallet.json', True)
        self.wallet_names_db = pickledb.load(f'{dir_path}/wallet_names.json', True)
        self.main_address = self.wallet_names_db.get('main_address')

        self.title("Denaro Wallet")
        self.geometry("800x600")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, expand=True)

        self.create_wallet_tab = ttk.Frame(self.notebook, width=800, height=600)
        self.send_tab = ttk.Frame(self.notebook, width=800, height=600)
        self.balance_tab = ttk.Frame(self.notebook, width=800, height=600)
        self.manage_wallets_tab = ttk.Frame(self.notebook, width=800, height=600)

        self.notebook.add(self.create_wallet_tab, text='Create Wallet')
        self.notebook.add(self.send_tab, text='Send')
        self.notebook.add(self.balance_tab, text='Balance')
        self.notebook.add(self.manage_wallets_tab, text='Manage Wallets')

        self.create_wallet_widgets()
        self.create_send_widgets()
        self.create_balance_widgets()
        self.create_manage_wallets_widgets()
        self.load_wallets()

    def create_manage_wallets_widgets(self):
        self.wallets_tree = ttk.Treeview(self.manage_wallets_tab, columns=("Name", "Address", "Main"), show='headings')
        self.wallets_tree.heading("Name", text="Name")
        self.wallets_tree.heading("Address", text="Address")
        self.wallets_tree.heading("Main", text="Main")
        self.wallets_tree.pack(fill="both", expand=True)

        set_main_button = ttk.Button(self.manage_wallets_tab, text="Set as Main", command=self.set_main_address)
        set_main_button.pack(pady=5)

        rename_button = ttk.Button(self.manage_wallets_tab, text="Rename Address", command=self.rename_address)
        rename_button.pack(pady=5)

        delete_button = ttk.Button(self.manage_wallets_tab, text="Delete Address", command=self.delete_address)
        delete_button.pack(pady=5)

        self.manage_wallets_status_label = ttk.Label(self.manage_wallets_tab, text="")
        self.manage_wallets_status_label.pack(pady=10)

        # Context menu for wallets_tree
        self.wallets_context_menu = tk.Menu(self, tearoff=0)
        self.wallets_context_menu.add_command(label="Copy Address", command=self.copy_address_to_clipboard)
        self.wallets_tree.bind("<Button-3>", self.show_wallets_context_menu)
        self.wallets_tree.bind("<Double-1>", self.copy_address_on_double_click)

    def create_wallet_widgets(self):
        create_wallet_button = ttk.Button(self.create_wallet_tab, text="Create New Address", command=self.create_wallet)
        create_wallet_button.pack(pady=20)

        self.wallet_info_label = ttk.Label(self.create_wallet_tab, text="")
        self.wallet_info_label.pack(pady=10)

    def create_send_widgets(self):
        # Wallet selection
        wallet_label = ttk.Label(self.send_tab, text="Select Sending Address:")
        wallet_label.pack(pady=5)
        self.send_address_combobox = ttk.Combobox(self.send_tab, width=57)
        self.send_address_combobox.pack(pady=5)
        self.update_send_addresses()

        recipient_label = ttk.Label(self.send_tab, text="Recipient Address:")
        recipient_label.pack(pady=5)
        self.recipient_entry = ttk.Entry(self.send_tab, width=60)
        self.recipient_entry.pack(pady=5)

        amount_label = ttk.Label(self.send_tab, text="Amount:")
        amount_label.pack(pady=5)
        self.amount_entry = ttk.Entry(self.send_tab, width=30)
        self.amount_entry.pack(pady=5)

        message_label = ttk.Label(self.send_tab, text="Message (optional):")
        message_label.pack(pady=5)
        self.message_entry = ttk.Entry(self.send_tab, width=60)
        self.message_entry.pack(pady=5)

        send_button = ttk.Button(self.send_tab, text="Send", command=self.send_transaction)
        send_button.pack(pady=20)

        self.send_status_label = ttk.Label(self.send_tab, text="")
        self.send_status_label.pack(pady=10)

    def set_main_address(self):
        selected_item = self.wallets_tree.focus()
        if not selected_item:
            self.manage_wallets_status_label.config(text="Please select an address.")
            return

        address = self.wallets_tree.item(selected_item)['values'][1]
        self.main_address = address
        self.wallet_names_db.set('main_address', address)
        self.wallet_names_db.dump()
        self.load_wallets()
        self.manage_wallets_status_label.config(text=f"'{address}' set as main address.")

    def rename_address(self):
        selected_item = self.wallets_tree.focus()
        if not selected_item:
            self.manage_wallets_status_label.config(text="Please select an address.")
            return

        address = self.wallets_tree.item(selected_item)['values'][1]
        old_name = self.wallet_names_db.get(address) or address

        new_name = simpledialog.askstring("Rename Address", f"Enter new name for '{old_name}':")
        if not new_name:
            return

        self.wallet_names_db.set(address, new_name)
        self.wallet_names_db.dump()
        self.load_wallets()
        self.manage_wallets_status_label.config(text=f"Address renamed to '{new_name}'.")

    def delete_address(self):
        selected_item = self.wallets_tree.focus()
        if not selected_item:
            self.manage_wallets_status_label.config(text="Please select an address.")
            return

        address = self.wallets_tree.item(selected_item)['values'][1]
        name = self.wallets_tree.item(selected_item)['values'][0]

        if messagebox.askyesno("Delete Address", f"Are you sure you want to delete '{name}' ({address})? This cannot be undone."):
            private_keys = self.wallet_db.get('private_keys') or []
            new_private_keys = []
            deleted_pk = None
            for pk in private_keys:
                current_address = point_to_string(keys.get_public_key(pk, CURVE))
                if current_address == address:
                    deleted_pk = pk
                else:
                    new_private_keys.append(pk)
            if deleted_pk:
                self.wallet_db.set('private_keys', new_private_keys)
                self.wallet_db.dump()
                self.wallet_names_db.rem(address)
                if self.main_address == address:
                    self.main_address = None
                    self.wallet_names_db.rem('main_address')
                self.wallet_names_db.dump()
                self.load_wallets()
                self.manage_wallets_status_label.config(text=f"Address '{name}' deleted.")
            else:
                self.manage_wallets_status_label.config(text=f"Error: Address '{name}' not found in wallet.json.")

    def show_wallets_context_menu(self, event):
        self.wallets_context_menu.post(event.x_root, event.y_root)

    def copy_address_on_double_click(self, event):
        selected_item = self.wallets_tree.focus()
        if not selected_item:
            return
        address = self.wallets_tree.item(selected_item)['values'][1]
        self.clipboard_clear()
        self.clipboard_append(address)
        self.manage_wallets_status_label.config(text=f"Address copied to clipboard: {address}")

    def copy_address_to_clipboard(self):
        selected_item = self.wallets_tree.focus()
        if not selected_item:
            return
        address = self.wallets_tree.item(selected_item)['values'][1]
        self.clipboard_clear()
        self.clipboard_append(address)

    def create_balance_widgets(self):
        refresh_button = ttk.Button(self.balance_tab, text="Refresh", command=self.refresh_balance)
        refresh_button.pack(pady=10)

        self.balance_tree = ttk.Treeview(self.balance_tab, columns=("Address", "Balance"), show='headings')
        self.balance_tree.heading("Address", text="Address")
        self.balance_tree.heading("Balance", text="Balance")
        self.balance_tree.pack(fill="both", expand=True)

        self.total_balance_label = ttk.Label(self.balance_tab, text="")
        self.total_balance_label.pack(pady=10)

    def create_wallet(self):
        db = pickledb.load(f'{dir_path}/wallet.json', True)
        private_keys = db.get('private_keys') or []
        private_key = keys.gen_private_key(CURVE)
        private_keys.append(private_key)
        db.set('private_keys', private_keys)

        public_key = keys.get_public_key(private_key, CURVE)
        address = point_to_string(public_key)

        self.wallet_info_label.config(text=f'''Private key: {hex(private_key)}
Address: {address}''')
        self.wallet_names_db.set(address, f"Wallet {len(private_keys)}")
        self.wallet_names_db.dump()
        self.load_wallets()
        self.update_send_addresses()

    def refresh_balance(self):
        self.balance_tree.delete(*self.balance_tree.get_children())
        db = pickledb.load(f'{dir_path}/wallet.json', True)
        private_keys = db.get('private_keys') or []
        total_balance = 0
        for private_key in private_keys:
            public_key = keys.get_public_key(private_key, CURVE)
            address = point_to_string(public_key)
            try:
                result = subprocess.run(["python3", f"{dir_path}/nodeless_wallet.py", "balance"], capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Error running nodeless_wallet.py balance:\n{result.stderr}")
                    self.balance_tree.insert("", "end", values=(address, f'Error: {result.stderr}'))
                    continue
                lines = result.stdout.splitlines()
                balance = 0.0
                # Find the balance for the current address
                for i, line in enumerate(lines):
                    if f"Address: {address}" in line:
                        # Assuming balance is 2 lines after address
                        balance_line = lines[i + 2]
                        balance_str = balance_line.split("Balance: ")[1].split(" ")[0]
                        balance = float(balance_str)
                        break
                total_balance += balance
                self.balance_tree.insert("", "end", values=(address, f'{balance} DEN'))
            except subprocess.CalledProcessError as e:
                print(traceback.format_exc())
                self.balance_tree.insert("", "end", values=(address, f'Error: {e.stderr}'))
            except Exception as e:
                print(traceback.format_exc())
        self.total_balance_label.config(text=f"Total Balance: {total_balance} DEN")

    def send_transaction(self):
        selected_address_name = self.send_address_combobox.get()
        if not selected_address_name:
            self.send_status_label.config(text="Please select a sending address.")
            return

        # Find the actual address from the name
        private_keys = self.wallet_db.get('private_keys') or []
        selected_address = None
        selected_private_key = None
        for pk in private_keys:
            address = point_to_string(keys.get_public_key(pk, CURVE))
            name = self.wallet_names_db.get(address) or address
            if name == selected_address_name:
                selected_address = address
                selected_private_key = hex(pk)
                break

        if not selected_address or not selected_private_key:
            self.send_status_label.config(text=f"Error: Could not find private key for {selected_address_name}")
            return

        recipient = self.recipient_entry.get()
        amount = self.amount_entry.get()
        message = self.message_entry.get()

        if not recipient or not amount:
            self.send_status_label.config(text="Recipient and amount are required.")
            return

        try:
            command = ["python3", f"{dir_path}/nodeless_wallet.py", "send", "-to", recipient, "-d", amount, "-pk", selected_private_key]
            if message:
                command.extend(["-m", message])
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error running nodeless_wallet.py send:\n{result.stderr}")
                self.send_status_label.config(text=f"Error: {result.stderr}")
                return
            self.send_status_label.config(text=result.stdout)
        except subprocess.CalledProcessError as e:
            print(traceback.format_exc())
            self.send_status_label.config(text=f"Error: {e.stderr}")
        except Exception as e:
            print(traceback.format_exc())

    def update_send_addresses(self):
        private_keys = self.wallet_db.get('private_keys') or []
        addresses = []
        for pk in private_keys:
            address = point_to_string(keys.get_public_key(pk, CURVE))
            name = self.wallet_names_db.get(address) or address
            addresses.append(name)
        self.send_address_combobox['values'] = addresses
        if addresses:
            if self.main_address:
                main_name = self.wallet_names_db.get(self.main_address) or self.main_address
                self.send_address_combobox.set(main_name)
            else:
                self.send_address_combobox.set(addresses[0])

    def load_wallets(self):
        self.wallets_tree.delete(*self.wallets_tree.get_children())
        private_keys = self.wallet_db.get('private_keys') or []
        for pk in private_keys:
            address = point_to_string(keys.get_public_key(pk, CURVE))
            name = self.wallet_names_db.get(address) or address
            is_main = "Yes" if address == self.main_address else "No"
            self.wallets_tree.insert("", "end", values=(name, address, is_main))
        private_keys = self.wallet_db.get('private_keys') or []
        for pk in private_keys:
            address = point_to_string(keys.get_public_key(pk, CURVE))
            name = self.wallet_names_db.get(address) or address
            is_main = "Yes" if address == self.main_address else "No"
            self.wallets_tree.insert("", "end", values=(name, address, is_main))

if __name__ == '__main__':
    app = WalletApp()
    app.mainloop()
