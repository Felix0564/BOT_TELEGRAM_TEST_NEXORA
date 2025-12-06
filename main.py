
import os
import json
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (Application,CommandHandler,MessageHandler,ConversationHandler,ContextTypes,filters,)

load_dotenv()

TOKEN = os.getenv("TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
ORDERS_FILE = "orders.json"

ITEM, QTY, ADDRESS, CONFIRM = range(4)

MENU = {
    "1": {"name": "Pizza Margherita", "price": 10000},
    "2": {"name": "Burger Classique", "price": 9000},
    "3": {"name": "Salade César", "price": 7000},
    "4": {"name": "Boisson (33cl)", "price": 2500},
}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bienvenue au restaurant Nexora !\n\n"
        "Commandes rapides :\n"
        "/menu - Voir notre menu\n"
        "/order - Passer une commande\n"
        "/help - Obtenir de l'aide\n\n"
        "Nous sommes heureux de vous servir."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/menu - Voir les plats et prix\n"
        "/order - Démarrer une commande guidée\n"
        "/cancel - Annuler la commande en cours\n"
        "Pour toute demande spéciale, contactez le restaurant."
    )

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = ["Notre menu :"]
    for key, item in MENU.items():
        lines.append(f"{key}. {item['name']} - {item['price']} FCFA")
    lines.append("\nPour commander rapidement : /order")
    await update.message.reply_text("\n".join(lines))


async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = ["Pour commander, indiquez le numéro de l'article :"]
    for key, item in MENU.items():
        lines.append(f"{key}. {item['name']} - {item['price']} FCFA")
    await update.message.reply_text("\n".join(lines))
    return ITEM

async def item_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text not in MENU:
        await update.message.reply_text("Numéro invalide. Merci d'indiquer le numéro de l'article.")
        return ITEM
    context.user_data["order"] = {"item_id": text, "item": MENU[text]["name"], "price": MENU[text]["price"]}
    await update.message.reply_text(f"Combien de {MENU[text]['name']} souhaitez-vous ?")
    return QTY

async def qty_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit() or int(text) <= 0:
        await update.message.reply_text("Quantité invalide. Indiquez un nombre entier positif.")
        return QTY
    qty = int(text)
    context.user_data["order"]["qty"] = qty
    total = qty * context.user_data["order"]["price"]
    context.user_data["order"]["total"] = total
    await update.message.reply_text("Indiquez l'adresse de livraison ou tapez 'retrait' pour retrait sur place.")
    return ADDRESS


async def address_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    address = update.message.text.strip()
    context.user_data["order"]["address"] = address
    order = context.user_data["order"]
    summary = (
        f"Résumé de la commande :\n"
        f"{order['qty']} x {order['item']} -> {order['total']:.2f} FCFA\n"
        f"Adresse / Option : {order['address']}\n\n"
        "Confirmez-vous la commande ? (oui / non)"
    )
    await update.message.reply_text(summary)
    return CONFIRM


async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    if text not in ("oui", "o", "yes", "y"):
        await update.message.reply_text("Commande annulée. Tapez /order pour recommencer.")
        context.user_data.pop("order", None)
        return ConversationHandler.END

    order = context.user_data.get("order")
    if not order:
        await update.message.reply_text("Aucun détail de commande trouvé. Tapez /order pour commencer.")
        return ConversationHandler.END
    
    saved = save_order(update.effective_user.id, update.effective_user.full_name, order)
    await update.message.reply_text(f"Merci ! Votre commande a été enregistrée (ID {saved}). Nous vous contacterons bientôt.")


    if ADMIN_ID:
        try:
            admin_msg = (
                f"Nouvelle commande #{saved}:\n"
                f"Client: {update.effective_user.full_name} (id: {update.effective_user.id})\n"
                f"{order['qty']} x {order['item']} -> {order['total']:.2f} FCFA\n"
                f"Adresse/Option: {order['address']}"
            )
            await context.bot.send_message(chat_id=int(ADMIN_ID), text=admin_msg)
        except Exception as e:
            logger.exception("Impossible de notifier l'admin : %s", e)

    context.user_data.pop("order", None)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("order", None)
    await update.message.reply_text("Opération annulée. Tapez /order pour recommencer.")
    return ConversationHandler.END


def save_order(user_id, user_name, order):
    
    try:
        if os.path.exists(ORDERS_FILE):
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []
    except Exception:
        data = []

    order_id = len(data) + 1
    record = {
        "id": order_id,
        "user_id": user_id,
        "user_name": user_name,
        "item": order["item"],
        "qty": order["qty"],
        "total": order["total"],
        "address": order["address"],
    }
    data.append(record)
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return order_id


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception update:", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text("Une erreur est survenue. Veuillez réessayer plus tard.")


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("TOKEN non défini dans le fichier .env")
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("order", order_start)],
        states={
            ITEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, item_chosen)],
            QTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, qty_received)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address_received)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_order)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="order_conversation",
        persistent=False,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(conv_handler)
    app.add_error_handler(error_handler)

    app.run_polling(poll_interval=3)



# import os
# from dotenv import load_dotenv
# from telegram.ext import Application , CommandHandler

# load_dotenv()

# token=os.getenv("TOKEN")

# async def start(update, context):
#     await update.message.reply_text("""Bienvenue au restaurant Nexora !\nQue souhaitez-vous commander ?
#                                     -/menu pour voir nos defferents menus """)
   
  

# if __name__ == '__main__':
#     app=Application.builder().token(token).build()
#     app.add_handler(CommandHandler("start", start))
#     app.run_polling(poll_interval=3)