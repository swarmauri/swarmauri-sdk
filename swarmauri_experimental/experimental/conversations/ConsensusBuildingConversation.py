from swarmauri.core.conversations.IConversation import IConversation
from swarmauri.core.messages.IMessage import IMessage


class ConsensusBuildingMessage(IMessage):
    def __init__(self, sender_id: str, content: str, message_type: str):
        self._sender_id = sender_id
        self._content = content
        self._role = 'consensus_message'
        self._message_type = message_type

    @property
    def role(self) -> str:
        return self._role

    @property
    def content(self) -> str:
        return self._content

    def as_dict(self) -> dict:
        return {
            "sender_id": self._sender_id,
            "content": self._content,
            "message_type": self._message_type
        }


class ConsensusBuildingConversation(IConversation):
    def __init__(self, topic: str, participants: list):
        self.topic = topic
        self.participants = participants  # List of agent IDs
        self._history = []  # Stores all messages exchanged in the conversation
        self.proposal_votes = {}  # Tracks votes for each proposal

    @property
    def history(self) -> list:
        return self._history

    def add_message(self, message: IMessage):
        if not isinstance(message, ConsensusBuildingMessage):
            raise ValueError("Only instances of ConsensusBuildingMessage are accepted")
        self._history.append(message)

    def get_last(self) -> IMessage:
        if self._history:
            return self._history[-1]
        return None

    def clear_history(self) -> None:
        self._history.clear()

    def as_dict(self) -> list:
        return [message.as_dict() for message in self._history]

    def initiate_consensus(self, initiator_id: str, proposal=None):
        """Starts the conversation with an initial proposal, if any."""
        initiate_message = ConsensusBuildingMessage(initiator_id, proposal, "InitiateConsensusMessage")
        self.add_message(initiate_message)

    def add_proposal(self, sender_id: str, proposal: str):
        """Adds a proposal to the conversation."""
        proposal_message = ConsensusBuildingMessage(sender_id, proposal, "ProposalMessage")
        self.add_message(proposal_message)

    def add_comment(self, sender_id: str, comment: str):
        """Adds a comment or feedback regarding a proposal."""
        comment_message = ConsensusBuildingMessage(sender_id, comment, "CommentMessage")
        self.add_message(comment_message)

    def vote(self, sender_id: str, vote: str):
        """Registers a vote for a given proposal."""
        vote_message = ConsensusBuildingMessage(sender_id, vote, "VoteMessage")
        self.add_message(vote_message)
        # Count the vote
        self.proposal_votes[vote] = self.proposal_votes.get(vote, 0) + 1

    def check_agreement(self):
        """
        Checks if there is a consensus on any proposal.
        A simple majority (>50% of the participants) is required for consensus.
        """
        consensus_threshold = len(self.participants) / 2  # Define consensus as a simple majority

        for proposal, votes in self.proposal_votes.items():
            if votes > consensus_threshold:
                # A consensus has been reached
                return True, f"Consensus reached on proposal: {proposal} with {votes} votes."

        # If no consensus is reached
        return False, "No consensus reached."