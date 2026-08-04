from enum import StrEnum


class ParserType(StrEnum):
    HTML = "html"
    BROWSER = "browser"
    MANUAL = "manual"
    DNS_EXPERIMENTAL = "dns_experimental"

class PriceCheckStatus(StrEnum):
    SUCCESS = "success"
    BLOCKED = "blocked"
    SELECTOR_NOT_FOUND = "selector_not_found"
    PRICE_NOT_FOUND = "price_not_found"
    NETWORK_ERROR = "network_error"
    MANUAL = "manual"