import discord
from discord import app_commands

TOKEN = "MTU2MTQ5MjMyMzY4MTE3NzYzMA.GREeel.46pQfo6GK4sya711p6Ss_gBtb3UXwxNpecuFF4"

ID_SALON_BIENVENUE = 1557976315800457254

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# Mémoire des invitations de chaque serveur : {id_serveur: {code: nombre_utilisations}}
cache_invitations = {}


async def charger_invitations(guild):
    try:
        invitations = await guild.invites()
        cache_invitations[guild.id] = {i.code: i.uses for i in invitations}
    except discord.Forbidden:
        print("Attention : le bot n'a pas la permission 'Gérer le serveur', impossible de lire les invitations.")
        cache_invitations[guild.id] = {}


async def envoyer_bienvenue(member):
    guild = member.guild
    salon = guild.get_channel(ID_SALON_BIENVENUE)
    if salon is None:
        print("ERREUR : salon de bienvenue introuvable. Vérifie l'ID du salon et que le bot peut le voir.")
        return

    # Cherche quelle invitation a été utilisée
    try:
        invitations = await guild.invites()
    except discord.Forbidden:
        invitations = []

    anciennes = cache_invitations.get(guild.id, {})
    invitation_utilisee = None
    for inv in invitations:
        if inv.uses > anciennes.get(inv.code, 0):
            invitation_utilisee = inv
            break
    cache_invitations[guild.id] = {i.code: i.uses for i in invitations}

    if invitation_utilisee is not None and invitation_utilisee.inviter is not None:
        inviteur = invitation_utilisee.inviter
        total = sum(
            i.uses for i in invitations
            if i.inviter is not None and i.inviter.id == inviteur.id
        )
        ligne_invitation = f"• 📩 Invitation : Tu as rejoint grâce à {inviteur.mention} 🎟️"
        ligne_total = f"• 🏆 Invitations : {inviteur.mention} compte maintenant {total} invitations !"
    else:
        ligne_invitation = "• 📩 Invitation : Tu as rejoint via un lien inconnu 🎟️"
        ligne_total = "• 🏆 Invitations : information indisponible"

    message = "\n".join([
        "💜 Bienvenue sur le serveur de Raitox !",
        f"Ravi de t'accueillir parmi nous, {member.mention} ! 🎉",
        "Tu viens de rejoindre la communauté officielle de Raitox 💜",
        "─── 📌 INFORMATIONS D'ARRIVÉE ───",
        f"• 👥 Effectif : Tu es notre {guild.member_count}ᵉ membre !",
        ligne_invitation,
        ligne_total,
        "─── 🚀 GUIDE DE DÉMARRAGE ───",
        "• 📜 Règlement : Consulte le salon <#1557976315980939285> et accepte le règlement pour naviguer sereinement sur le serveur.",
        "• 🎫 Besoin d'aide ? L'équipe Staff reste à ta disposition via le salon : <#1557976317339766806>",
    ])

    try:
        await salon.send(message)
        print("Message de bienvenue envoyé pour :", member)
    except discord.Forbidden:
        print("ERREUR : le bot n'a pas la permission d'écrire dans le salon de bienvenue.")


@bot.event
async def on_ready():
    await tree.sync()
    for guild in bot.guilds:
        await charger_invitations(guild)
    print("Le bot est connecté :", bot.user)


@bot.event
async def on_invite_create(invite):
    cache_invitations.setdefault(invite.guild.id, {})[invite.code] = invite.uses


@bot.event
async def on_invite_delete(invite):
    cache_invitations.get(invite.guild.id, {}).pop(invite.code, None)


@bot.event
async def on_member_join(member):
    print("Nouveau membre détecté :", member)
    await envoyer_bienvenue(member)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.lower() == "salut":
        await message.channel.send("Salut !")


@tree.command(name="ping", description="Teste si le bot répond")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong !")


@tree.command(name="test_bienvenue", description="Simule l'arrivée d'un membre (test)")
@app_commands.default_permissions(administrator=True)
async def test_bienvenue(interaction: discord.Interaction):
    await interaction.response.send_message("Test envoyé dans le salon de bienvenue.", ephemeral=True)
    await envoyer_bienvenue(interaction.user)


bot.run(TOKEN)