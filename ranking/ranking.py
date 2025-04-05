import discord
from discord.ext import commands
import requests

class RankingBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roblosecurity = "=_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_D96F58476F35D0636952389B33D13A70CF27BD94C0E2B5C6E04EC8F5EA12CE59DE2BCE35147253298D20098D3AD24291FA6CE95A4BDA195165377A40F5A525A5B743E0DC7D3CFD23BD45857507C4D7918836188898C778B7373544B3A6F36DFEE90D51BAEA678C66C7F20A9FB03461D6BA305E2DD6E11AE5E913484918F77F8EAC97C121C895F0B4C87ABF79B79809E5ADDB7B8288079B44C74B8684D853F1FAA6A5BAFF7CFF23F58A6D6870649DF51436D871443D469901E1A8E77343EE81CC24DF160A1C2EFDBB1741A2765117F62D65DD8409A2E378BFAA9CDB8074CAF5AB9FC00CFA8ACB9109724EE18489F19E387A1564245E130754D9EA8FD1141C8F339A2CA54826C93A4F6CC17BC1352D0E3EEE5E7D66DF1B7108C909C4970E3EAEA2545E212977E3CDAEE54C51FEEC006F661897814F45157F23F56835070452C6D547D40270FAA6C434CEA887FB9C1FBFC9E04783387E0F2C711691129B4D8BA9836616EC9C6F7E9C8A186DE2E4143C91C6F3682F272A59BFCD35E709760C4BB0974E0DA9A4A32124D821F6D14C1B1C68DABD9B98447D4E7BA330F3085CA171763FEA29019061715785F1AD430CCCB700ACA88CD25BDA8A315CDBBF79D38B58471C0C2619143FC7C7ED821C7BA99C99835EAB1958DF5521A545CA0945B4C8C084131999A03BA34B804302742C127A72FC0D651FD94AF8B0CC8D0F413F35BF26A8B81A4EDF450F6C6CE17516630307922ABEE018516A1DA9942BF7EED0DE3E99FB0A21676B021647C8F851362ED8EAB445C7858D3BF2F8F19F9AC6EBEED1F0F588FAD646063B997F7A51D244C3CD9461C7DBBCF3362F9C07AED9B57E4A7FE63968DF9A11E2277789DB1B2885A4B2D78441F7825586C0C7FF95EA4793C77EEB7775CE0DC098A49BA3A6A3F7613803100E80362FBF9B63C4DF79408FA6FA6D938E9F4BFB80FA1921B7A769BED9307F0B99E252E1788F632C3DE274372994555740B018B4ABE43852BACC4693367EE4CF397726568F34D0AA245BA8707C9B724B426A6808BD353D99223D6C1659654655D7693D19851B127ABE8E87B61B0AEF70B50E9FB8C33A9F36F38A807146DFB79A68915F47CE4FDC60C9CBE9DAE81ACC939763B9CCCC1FB629B79181823359AE66D8B5C509CDC62B"  # Replace with your actual cookie
        self.headers = {
            "Cookie": f".ROBLOSECURITY={self.roblosecurity}",
            "Content-Type": "application/json"
        }

    def get_csrf_token(self):
        """Fetch a new CSRF token from Roblox."""
        response = requests.post("https://auth.roblox.com/v2/logout", headers=self.headers)
        token = response.headers.get("x-csrf-token")
        if token:
            self.headers["X-CSRF-TOKEN"] = token
            return True
        return False

    @commands.command(name="ranking-join")
    @commands.has_permissions(administrator=True)
    async def ranking_join(self, ctx, group_id: int):
        """Joins a Roblox group using group ID (Admins only)."""
        if not self.get_csrf_token():
            await ctx.send("Failed to get CSRF token.")
            return

        url = f"https://groups.roblox.com/v1/groups/{group_id}/users"
        payload = { "groupId": group_id }

        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code == 200:
            await ctx.send(f"Successfully joined group `{group_id}`!")
        else:
            await ctx.send(
                f"Failed to join group `{group_id}`.\n"
                f"Status: {response.status_code}\n"
                f"Response: {response.text}"
            )

    @commands.command(name="ranking-leave")
    @commands.has_permissions(administrator=True)
    async def ranking_leave(self, ctx, group_id: int):
        """Leaves a Roblox group using group ID (Admins only)."""
        if not self.get_csrf_token():
            await ctx.send("Failed to get CSRF token.")
            return

        url = f"https://groups.roblox.com/v1/groups/{group_id}/users/leave"

        response = requests.post(url, headers=self.headers)

        if response.status_code == 200:
            await ctx.send(f"Successfully left group `{group_id}`.")
        else:
            await ctx.send(
                f"Failed to leave group `{group_id}`.\n"
                f"Status: {response.status_code}\n"
                f"Response: {response.text}"
            )

    @ranking_join.error
    @ranking_leave.error
    async def permission_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You must be an **admin** to use this command.")

async def setup(bot):
    await bot.add_cog(RankingBot(bot))
