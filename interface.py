import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from PIL.Image import Resampling
from pylightxl import readxl
from os import path

import os
import price_scrapper as pricey
import Case_Skins as cls
import web_scrapper as cs_scrp
import get_offer_alg as alg
import save_to_db as save

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

global skin_in, skin_out_1, skin_out_2, skin_out_3

def updateDisplay(myString):
    displayVar.set(displayVar.get() + '\n' + myString)

def extract_skins(event):
    # Deactivate button
    btn_UpdateDB['state'] = 'disabled'
    btn_UpdateDB.unbind("<Button-1>")
    # Clear log window
    displayVar.set('')
    window.update()

    # Main function
    Cases = cs_scrp.extract_from_cases('https://csgostash.com/containers/skin-cases', displayVar, window)
    save.to_xlsx(Cases, 'Files/Skin_names.xlsx', False)

    # Reactivate button
    btn_UpdateDB['state'] = 'active'
    btn_UpdateDB.bind("<Button-1>", extract_skins)

    # Activate the price update button if it was disabled
    btn_UpdatePrices['state'] = 'active'
    btn_UpdatePrices.bind("<Button-1>", extract_prices)

def extract_prices(event):
    # Deactivate button
    btn_UpdatePrices['state'] = 'disabled'
    btn_UpdatePrices.unbind("<Button-1>")

    # Clear log window
    displayVar.set('')
    window.update()

    # Main function
    db = readxl('Files/Skin_names.xlsx')
    sheet_names = db.ws_names

    for sheet in sheet_names[1:]:
        ObjCase = cls.Case()
        ObjCase.name = sheet
        alg.read_xl(db, sheet, ObjCase)
        Cases.append(ObjCase)

    pricey.extract_prices('Files/Skin_names.xlsx', 'Files/Skin_prices.xlsx', displayVar, window)

    # Reactivate button
    btn_UpdatePrices['state'] = 'active'
    btn_UpdatePrices.bind("<Button-1>", extract_prices)

    # Activate buttons for searching offers
    btn_risk1.config(background='gold')
    btn_risk1['state'] = 'active'
    btn_risk1.bind("<Button-1>", lambda event, risk=1: search_offer(event, risk))

    btn_risk2.config(bg='gold')
    btn_risk2['state'] = 'active'
    btn_risk2.bind("<Button-1>", lambda event, risk=2: search_offer(event, risk))

    btn_risk3.config(bg='gold')
    btn_risk3['state'] = 'active'
    btn_risk3.bind("<Button-1>", lambda event, risk=3: search_offer(event, risk))

def get_n_resize(skin_name):
    skin_mare = Image.open(f'Files/Skins/{skin_name}.png')
    skin_mare = skin_mare.resize((94, 71), Image.LANCZOS)
    skin = ImageTk.PhotoImage(skin_mare)
    return skin

def print_trade_in(skin_in):
    x = 15
    y = 390

    for i in range(0, 10):
        skin_in_label = tk.Label(main_frame.scrollable_frame, image=skin_in, background='gray63', width=108, height=108)

        if i == 5:
            y = 505
            x = 15

        skin_in_label.place(x=x, y=y)
        x += 115

def search_offer(event, risk):
    # Clear previous trade-in items
    for widget in main_frame.scrollable_frame.winfo_children():
        if isinstance(widget, tk.Label) and widget != logo_panel:
            widget.destroy()

    deal = alg.get_offer('Files/Skin_prices.xlsx', 0, 0)
    
    # Display the 10 trade-in items
    x, y = 15, 390
    for i in range(10):
        skin_in = get_n_resize(deal[1].weapon + ' ' + deal[1].name)
        skin_in_label = tk.Label(main_frame.scrollable_frame, image=skin_in, background='gray63', width=108, height=108)
        skin_in_label.image = skin_in  # Keep a reference to avoid garbage collection
        skin_in_label.place(x=x, y=y)

        # Display price, cost, and quality under each skin
        skin_info = f"Name: {deal[1].name}\nCost: {deal[1].prices[deal[2]]}$\nQuality: {alg.num_to_quality(deal[2])}"
        skin_info_label = tk.Label(main_frame.scrollable_frame, text=skin_info, bg='gray63', fg='black', font=('Montserrat Black', 10), justify='left')
        skin_info_label.place(x=x, y=y + 120)

        if i == 4:
            y = 505
            x = 15
        else:
            x += 115

    # Create a scrollable frame for outcomes
    outcome_frame = ScrollableFrame(main_frame.scrollable_frame)
    outcome_frame.place(x=15, y=620, width=870, height=360)

    # Adjust layout and add outcomes to the scrollable frame
    invalid_values = ['N/A', ' ', '']
    for idx, outcome in enumerate(deal[4]):
        skin_out_image = get_n_resize(outcome.weapon + ' ' + outcome.name)
        skin_out_q = alg.num_to_quality(deal[2] + deal[3])
        price_out = outcome.prices[deal[2] + deal[3]] if outcome.prices[deal[2] + deal[3]] not in invalid_values else '-'

        skin_out_data = tk.Label(outcome_frame.scrollable_frame, image=skin_out_image,
                                 text=' ' + outcome.name + '\n PRICE: ' + price_out + '$\n Q: ' + skin_out_q,
                                 font=('Montserrat Black', 16), justify='left', fg='red4', background='brown1', width=350, height=150,  # Increased dimensions
                                 compound='left')
        skin_out_data.image = skin_out_image  # Keep a reference to avoid garbage collection
        row = idx // 2
        column = idx % 2
        skin_out_data.grid(row=row, column=column, padx=5, pady=5)
    
    # Calculate and display the total, max loss, and max win
    max_loss = alg.cheapest_skin(deal[4], deal[2] + deal[3])
    max_win = alg.expensive_skin(deal[4], deal[2] + deal[3])
    max_loss_f = float(max_loss.prices[deal[2] + deal[3]]) if max_loss != -1 else 0
    max_win_f = float(max_win.prices[deal[2] + deal[3]]) if max_win != -1 else 0
    total = round(float(deal[1].prices[deal[2]]) * 10, 3)

    select_risk = tk.Text(main_frame.scrollable_frame, font=('Montserrat Black', 21), bd=0, fg='gray34', bg='gray80', width=15, height=3)
    select_risk.tag_configure('center', justify='center')
    select_risk.insert('1.0', 'TOTAL: ' + str(total) + '$\n'
                       + 'MAX LOSS: ' + str(round(total - max_loss_f, 2)) + '$\n'
                       + 'MAX WIN: ' + str(round(max_win_f - total, 2)) + '$')
    select_risk.tag_add('center', '1.0', 'end')
    select_risk.place(x=650, y=390)

window = tk.Tk()
window.geometry('900x1250')
window.title("CS:GO Trade-up Scrapper")
window.resizable(True, True)

main_frame = ScrollableFrame(window)
main_frame.pack(fill="both", expand=True)

path_logo = 'Files/logo.png'

pixel = tk.PhotoImage(width=1, height=1)

frame = tk.Frame(main_frame.scrollable_frame, bg='gray15', height=2000, width=1200)
frame.pack()

image = Image.open(path_logo)
logo = ImageTk.PhotoImage(image)

logo_panel = tk.Label(frame, image=logo, bd=0)
logo_panel.place(x=305, y=13)

# region Main Buttons

btn_UpdateDB = tk.Button(frame, text="EXTRACT\nNAMES", image=pixel, bd=0, background='gray63', fg='gray15',
                         font=('Montserrat Black', 12), width=153, height=63, compound="c")
btn_UpdateDB.place(x=82, y=208)

btn_UpdatePrices = tk.Button(frame, text="EXTRACT\nPRICES", image=pixel, bd=0, background='gray63', fg='gray15',
                             font=('Montserrat Black', 12), width=153, height=63, compound="c")
btn_UpdatePrices.place(x=82, y=284)

if not path.exists('Files/Skin_names.xlsx'):
    btn_UpdatePrices['state'] = 'disabled'
    btn_UpdatePrices.unbind("<Button-1>")

btn_UpdateDB.bind("<Button-1>", extract_skins)
btn_UpdatePrices.bind("<Button-1>", extract_prices)

# endregion

# region Log Viewer Window
displayVar = tk.StringVar()
displayLab = tk.Label(frame, textvariable=displayVar, height=10, width=55, justify='left', anchor='sw')
displayLab.place(x=248, y=208)
#endregion

# region Select Risk Level 

select_risk = tk.Text(frame, font=('Montserrat Black', 25), bd=0, fg='tan2', bg='gray15', width=10, height=2)
select_risk.tag_configure('center', justify='center')
select_risk.insert('1.0', 'SELECT\nRISK LEVEL')
select_risk.tag_add('center', '1.0', 'end')
select_risk.place(x=645, y=205)


# region Risk Buttons

btn_risk1 = tk.Button(frame, text="1", image=pixel, relief='solid', bd=0, bg='gold', fg='black',
                      font=('Montserrat Black', 19), width=35, height=35, compound="c")
btn_risk1.place(x=680, y=310)
btn_risk1.bind("<Button-1>", lambda event, risk=1: search_offer(event, risk))

btn_risk2 = tk.Button(frame, text="2", image=pixel, relief='solid', bd=0, bg='gold', fg='black',
                      font=('Montserrat Black', 19), width=35, height=35, compound="c")
btn_risk2.place(x=740, y=310)
btn_risk2.bind("<Button-1>", lambda event, risk=2: search_offer(event, risk))

btn_risk3 = tk.Button(frame, text="3", image=pixel, relief='solid', bd=0, bg='gold', fg='black',
                      font=('Montserrat Black', 19), width=35, height=35, compound="c")
btn_risk3.place(x=800, y=310)
btn_risk3.bind("<Button-1>", lambda event, risk=3: search_offer(event, risk))

if not path.exists('Files/Skin_prices.xlsx'):
    btn_risk1['state'] = 'disabled'
    btn_risk1.unbind("<Button-1>")

    btn_risk2['state'] = 'disabled'
    btn_risk2.unbind("<Button-1>")

    btn_risk3['state'] = 'disabled'
    btn_risk3.unbind("<Button-1>")

# endregion

bg_trade_up = tk.Label(frame, image=pixel, background='gray80', width=930, height=360)
bg_trade_up.place(x=0, y=379)

Cases = []

window.mainloop()