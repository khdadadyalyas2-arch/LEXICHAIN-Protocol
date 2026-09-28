"""
LEXICHAIN Protocol - Autonomous Ethereum Arbitration & Legal Disputer Agent
BLI LegalTech Hackathon 2
License: MIT
"""

import time
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="LexiChain Arbitration Engine",
    description="Decentralized Smart Contract Dispute Resolution & AI Arbitrator",
    version="1.0.0"
)

disputes_db: Dict[str, dict] = {}
audit_trail: List[dict] = []


class DisputeSubmission(BaseModel):
    contract_address: str = Field(..., description="Target Smart Contract Address")
    claimant_address: str = Field(..., description="Claimant Wallet Address")
    respondent_address: str = Field(..., description="Respondent Wallet Address")
    disputed_amount_eth: float = Field(..., gt=0, description="Disputed Amount in ETH")
    evidence_uri: str = Field(..., description="IPFS URI to evidentiary documentation")
    legal_claim_type: str = Field(..., description="Breach of Escrow / Milestone Default / Oracle Failure")


class EvidenceEvaluationRequest(BaseModel):
    dispute_id: str = Field(..., description="Dispute Case Reference ID")
    arbitrator_agent_id: str = Field(..., description="Decentralized Autonomous Arbitrator ID")
    ruling_decision: str = Field(..., description="FAVOR_CLAIMANT / FAVOR_RESPONDENT / SPLIT_SETTLEMENT")
    rationale: str = Field(..., description="Legal and logical justification")


@app.get("/")
def root():
    return {
        "protocol": "LexiChain Arbitration Engine",
        "status": "OPERATIONAL",
        "supported_chain": "Ethereum / EVM",
        "pending_disputes": len([d for d in disputes_db.values() if d["status"] == "PENDING_ARBITRATION"])
    }


@app.post("/api/v1/disputes/file", status_code=status.HTTP_201_CREATED)
def file_dispute(submission: DisputeSubmission):
    dispute_id = f"dsp_{int(time.time() * 1000)}"
    record = {
        "dispute_id": dispute_id,
        "contract_address": submission.contract_address,
        "claimant": submission.claimant_address,
        "respondent": submission.respondent_address,
        "amount_eth": submission.disputed_amount_eth,
        "evidence_uri": submission.evidence_uri,
        "claim_type": submission.legal_claim_type,
        "status": "PENDING_ARBITRATION",
        "filed_at": int(time.time()),
        "verdict": None
    }
    disputes_db[dispute_id] = record
    return {"status": "SUCCESS", "dispute": record}


@app.post("/api/v1/arbitration/verdict")
def deliver_verdict(req: EvidenceEvaluationRequest):
    if req.dispute_id not in disputes_db:
        raise HTTPException(status_code=404, detail="Dispute case not found")
        
    dispute = disputes_db[req.dispute_id]
    if dispute["status"] == "SETTLED":
        raise HTTPException(status_code=400, detail="Dispute already settled")
        
    verdict = {
        "verdict_id": f"v_{int(time.time() * 1000)}",
        "dispute_id": req.dispute_id,
        "arbitrator_agent": req.arbitrator_agent_id,
        "decision": req.ruling_decision,
        "rationale": req.rationale,
        "settled_at": int(time.time())
    }
    
    dispute["status"] = "SETTLED"
    dispute["verdict"] = verdict
    audit_trail.append(verdict)
    
    return {"status": "VERDICT_ISSUED", "verdict": verdict}


@app.get("/api/v1/disputes")
def list_disputes():
    return {"total": len(disputes_db), "disputes": list(disputes_db.values())}


@app.get("/api/v1/audit/verdicts")
def get_verdict_logs():
    return {"total": len(audit_trail), "verdicts": audit_trail}
