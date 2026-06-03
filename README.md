💰 Adaptive Budget Optimization Agent
An intelligent budget monitoring agent built for Malaysian university students using LangGraph and a hybrid BDI architecture. Reads your spending transactions, detects overspending, and automatically reallocates budget from wants to needs to keep you on track.

✨ Technologies
* `Python`
* `LangGraph`
* `Google Gemini AI`
* `pandas`

🚀 Features
* BDI agent pipeline: Perception, Reasoning, Planning, and Effector nodes wired as a stateful graph
* Automatically detects critical overspending and reallocates surplus from want categories to cover need deficits
* Gemini-powered advice in Malaysian English — friendly, casual, and actually useful
* Rule-based fallback messages if no API key is configured
* Covers 5 spending categories: Makanan, Pengangkutan, Hiburan, Keperluan, and Shopping

📍 The Process
Malaysian students are notoriously bad at tracking money, not because they don't care, but because no tool actually fits how they spend. Mamak runs, Grab rides, last minute shopping before raya, it adds up fast. I wanted to build an agent that doesn't just warn you, but actually fixes the problem by moving budget around intelligently. The BDI model made sense here: the agent perceives your transactions, reasons about which categories are in trouble, plans a reallocation if things are critical, then talks to you like a friend would. Wrapping it in LangGraph kept the workflow clean and easy to follow. Getting Gemini to sound like an actual Malaysian instead of a corporate chatbot took some prompt tuning too.

🚦 Running the Project
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Add your Gemini API key to `main.py`
4. Place your transaction data in `data/transactions.csv`
5. Run the agent: `python main.py`
