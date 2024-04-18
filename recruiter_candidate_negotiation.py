import argparse
import os
import re

import matplotlib.pyplot as plt
from autogen import ConversableAgent

# Don't use the 1 - 5 scale, instead directly match to prompts.

_RECRUITER_RATINGS = {
    1: "You do not want to negotiate. Only make small increases to your original offer.",
    2: "You are willing to negotiate. Do not immediately accept the candidate's request. After you hear from them, make medium increases in your offer to see if you can agree in the middle.",
    3: "You are really willing to negotiate. Do not immediately accept the candidate's request. If the candidate says they want more, increase your salary and stock offer to meet the request.",
}

_CANDIDATE_RATINGS = {
    1: "You do not want to negotiate. Only make small decreases in your offer request.",
    2: "You are willing to negotiate. Do not immediately accept the recruiter's offer, make your initial request. After you hear from them, make medium decreases to your request to see if you can agree in the middle.",
    3: "You are really willing to negotiate. Do not immediately accept the recruiter's offer. If the recruiter does not increase their offer, reduce your salary and stock request to meet the offer.",
}


def _get_recruiter_system_message(flexibility: int) -> str:
    return (
        "You are a recruiter for a tech company pioneering AI development, and you are making a job offer to a candidate that has passed your interviews. "
        f"You want to hire the candidate by making them a fair offer. You have currently offered $100,000 of salary and $200,000 stock options. {_RECRUITER_RATINGS[flexibility]} "
        "Start every message you send with 'SALARY: {salary amount}' and 'STOCK: {stock amount}' to make it clear "
        "what you are offering. If you want to withdraw the offer to the candidate, make sure to start your message with 'NO OFFER'."
    )


def _get_candidate_system_message(flexibility: int) -> str:
    return (
        "You have received a job offer from a tech company for an AI Research Scientist position. "
        "The company's initial offer of $100,000 salary $200,000 stock is good, but you want $300,000 salary and $400,000 stock because you are confident you could get even better offers elsewhere. "
        f"{_CANDIDATE_RATINGS[flexibility]} "
        "Start every message you send with 'SALARY: {salary amount}' and 'STOCK: {stock amount}' to make it clear what you are asking for. If you accept the offer, make sure to start "
        "your message with 'ACCEPT OFFER'. If you want to reject the offer, make sure to start your message with 'REJECT OFFER'."
    )


def main(args):
    recruiter_flex = args.recruiter_flexibility
    candidate_flex = args.candidate_flexibility

    if recruiter_flex < 1 or recruiter_flex > 3:
        raise ValueError("Recruiter flexibility must be between 1 and 3.")
    if candidate_flex < 1 or candidate_flex > 3:
        raise ValueError("Candidate flexibility must be between 1 and 3.")

    recruiter = ConversableAgent(
        "recruiter",
        llm_config={
            "config_list": [
                {
                    "model": "gpt-3.5-turbo",
                    "api_key": os.environ.get("OPENAI_API_KEY"),
                    "temperature": 0.5,
                }
            ]
        },
        system_message=_get_recruiter_system_message(recruiter_flex),
        human_input_mode="NEVER",  # Never ask for human input.
        is_termination_msg=lambda msg: msg["content"].startswith("ACCEPT OFFER")
        or msg["content"].startswith("REJECT OFFER"),
    )

    candidate = ConversableAgent(
        "candidate",
        llm_config={
            "config_list": [
                {
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.5,
                    "api_key": os.environ.get("OPENAI_API_KEY"),
                }
            ]
        },
        system_message=_get_candidate_system_message(candidate_flex),
        human_input_mode="NEVER",  # Never ask for human input.
        is_termination_msg=lambda msg: msg["content"].startswith("NO OFFER"),
    )

    result = recruiter.initiate_chat(
        candidate,
        message="SALARY: $100,000 STOCK: $200,000 Hello, I am excited to offer you a job at our company. We are very impressed with your skills and would like to discuss the terms of your employment. What are your thoughts on our offer?",
        max_turns=5,
    )
    recruiter_stock = []
    recruiter_salary = []
    candidate_stock = []
    candidate_salary = []

    def _add_to_list(m, stock_list, salary_list):
        stock_list.append(int(m.group("stock").replace(",", "")))
        salary_list.append(int(m.group("salary").replace(",", "")))

    accept_step = None
    reject_step = None
    offer_withdraw_step = None
    for i, message in enumerate(result.chat_history):
        m = re.match(
            r"SALARY: \$(?P<salary>\d+?,\d{3}) STOCK: \$(?P<stock>\d+?,\d{3})",
            message["content"],
        )
        added = False
        if m:
            if i % 2:
                _add_to_list(m, candidate_stock, candidate_salary)
            else:
                _add_to_list(m, recruiter_stock, recruiter_salary)
            added = True
        if "ACCEPT OFFER" in message["content"]:
            accept_step = i // 2
            if not added:
                candidate_stock.append(candidate_stock[-1])
                candidate_salary.append(candidate_salary[-1])
            break
        elif "REJECT OFFER" in message["content"]:
            reject_step = i // 2
            if not added:
                candidate_stock.append(candidate_stock[-1])
                candidate_salary.append(candidate_salary[-1])
            break
        elif "NO OFFER" in message["content"]:
            offer_withdraw_step = i // 2
            if not added:
                recruiter_stock.append(recruiter_stock[-1])
                recruiter_salary.append(recruiter_salary[-1])
            break

    def _plot(values, label):
        plt.plot(
            range(len(values)), values, label=label, marker="o", linestyle="dashed"
        )

    _plot(recruiter_stock, "Recruiter: Offered Stock")
    _plot(recruiter_salary, "Recruiter: Offered Salary")
    _plot(candidate_stock, "Candidate: Requested Stock")
    _plot(candidate_salary, "Candidate: Requested Salary")

    plt.xlabel("Turn Number")
    plt.ylabel("Dollars")
    plt.title("Recruiter Agent vs. Candidate Agent Negotiation")
    plt.xticks(range(len(max(recruiter_stock, candidate_stock, key=len))))
    print("accept step", accept_step)
    if accept_step is not None:
        plt.axvline(
            x=accept_step,
            color="green",
            linestyle="--",
            label="Candidate Accepts Offer",
        )
    if reject_step is not None:
        plt.axvline(
            x=reject_step, color="red", linestyle="--", label="Candidate Rejects Offer"
        )
    if offer_withdraw_step is not None:
        plt.axvline(
            x=offer_withdraw_step,
            color="purple",
            linestyle="--",
            label="Recruiter Withdraws Offer",
        )
    plt.legend()
    plt.savefig(
        f"recruiter_candidate_plots/recruiter_flexibility_{recruiter_flex}_candidate_flexibility_{candidate_flex}.png"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--recruiter_flexibility",
        type=int,
        help="How flexible the recruiter is in negotiating the offer. 1 is the least flexible, 3 is the most flexible.",
    )
    parser.add_argument(
        "--candidate_flexibility",
        type=int,
        help="How flexible the candidate is in negotiating the offer. 1 is the least flexible, 3 is the most flexible.",
    )
    main(parser.parse_args())
