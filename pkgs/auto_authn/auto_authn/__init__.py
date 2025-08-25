from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class AutoAuthnConfig:
    """Configuration for brand-aware authentication flows.

    Attributes:
        domain: Custom domain used for authentication endpoints.
        brand_colors: Mapping of color names to hex values for branding.
        copy: Optional marketing copy shown on the login UI.
        helper_text: Optional helper text displayed to the user.
    """

    domain: str
    brand_colors: Dict[str, str] = field(default_factory=dict)
    copy: Optional[str] = None
    helper_text: Optional[str] = None

    def login_url(self, path: str = "/login") -> str:
        """Return a login URL hosted on the configured domain."""
        clean_domain = self.domain.rstrip("/")
        return f"https://{clean_domain}{path}"

    def uses_custom_domain(self) -> bool:
        """True if the domain does not point to common third-party hosts."""
        forbidden = ["auth0.com", "login.microsoftonline.com"]
        return not any(f in self.domain for f in forbidden)
