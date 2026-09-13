"""
CampaignStore — in-memory campaign registry.

Stores CampaignPackage objects by ID. This is the persistence layer for
Phase 1-4. Phase 5+ will replace this with a proper database-backed store
(PostgreSQL via Supabase) without changing the interface.

Design notes:
- Interface-first: the API router and services call store.save() / store.get()
  regardless of whether the implementation is in-memory or DB-backed.
- Thread safety: asyncio is single-threaded, so a plain dict is safe for
  async FastAPI. If we later add workers, this becomes an AsyncRedis client.
- No eviction policy needed in Phase 1 (academic demo scope).
"""
from __future__ import annotations

import logging
from typing import Optional

from packages.shared.errors import BrandOSError
from packages.shared.models.campaign import CampaignPackage

logger = logging.getLogger(__name__)


class CampaignNotFoundError(BrandOSError):
    """Raised when a campaign ID does not exist in the store."""


class CampaignStore:
    """In-memory store for CampaignPackage objects.

    This is intentionally a thin wrapper around a dict so it can be swapped
    for a database-backed implementation in Phase 5 by only changing this file.

    Usage:
        store = CampaignStore()
        await store.save(package)
        package = await store.get(package.id)
        all_packages = await store.list_all()
    """

    def __init__(self) -> None:
        self._store: dict[str, CampaignPackage] = {}
        logger.debug("CampaignStore initialised (in-memory)")

    async def save(self, package: CampaignPackage) -> CampaignPackage:
        """Persist a CampaignPackage.

        If a package with the same ID already exists, it is overwritten.
        This is intentional — callers use save() for both create and update.

        Args:
            package: The campaign package to persist.

        Returns:
            The saved package (same object, returned for chaining convenience).
        """
        self._store[package.id] = package
        logger.info("Saved campaign package id=%s status=%s", package.id, package.status)
        return package

    async def get(self, campaign_id: str) -> CampaignPackage:
        """Retrieve a CampaignPackage by ID.

        Args:
            campaign_id: The UUID of the campaign.

        Returns:
            The matching CampaignPackage.

        Raises:
            CampaignNotFoundError: If no campaign with this ID exists.
        """
        package = self._store.get(campaign_id)
        if package is None:
            raise CampaignNotFoundError(
                message=f"Campaign not found: {campaign_id}",
                detail="The campaign may not have been created yet, or the ID is incorrect.",
            )
        return package

    async def list_all(self) -> list[CampaignPackage]:
        """Return all stored campaigns, ordered by creation time (newest first).

        Returns:
            A list of CampaignPackage objects.
        """
        return sorted(
            self._store.values(),
            key=lambda p: p.created_at,
            reverse=True,
        )

    def __len__(self) -> int:
        return len(self._store)
