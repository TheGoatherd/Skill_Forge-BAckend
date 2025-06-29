import motor.motor_asyncio
import os 
from dotenv import load_dotenv

load_dotenv() # Load .env variables

MONGO_URI =os.getenv("MONGO_URI","mongodb+srv://iamankit4435:@Totaloverdose@skillforge-database.vwfthj6.mongodb.net/skillforge?retryWrites=true&w=majority")
client=motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client["skillforge_database"] 