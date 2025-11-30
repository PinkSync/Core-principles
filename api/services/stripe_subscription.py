"""Stripe subscription service for ASL Biometric System."""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import os

from ..models.subscription import (
    PricingPlan,
    CreateCheckoutRequest,
    CheckoutSessionResponse,
    SubscriptionInfo,
    SubscriptionStatus,
    UsageReport,
    PortalSessionResponse,
    PRICING_PLANS
)

logger = logging.getLogger(__name__)


class StripeSubscriptionService:
    """
    Stripe subscription management service.
    
    Handles subscription creation, management, and usage tracking
    for the ASL Biometric verification platform.
    """
    
    def __init__(self):
        """Initialize Stripe service."""
        self.stripe_api_key = os.environ.get("STRIPE_SECRET_KEY")
        self.stripe_webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
        self._stripe = None
        
        # In-memory storage for demo (use database in production)
        self.subscriptions: Dict[str, SubscriptionInfo] = {}
        self.usage: Dict[str, UsageReport] = {}
        
        self._initialize_stripe()
    
    def _initialize_stripe(self) -> None:
        """Initialize Stripe SDK if API key is available."""
        if self.stripe_api_key:
            try:
                import stripe
                stripe.api_key = self.stripe_api_key
                self._stripe = stripe
                logger.info("Stripe initialized successfully")
            except ImportError:
                logger.warning("Stripe package not installed")
        else:
            logger.info("Running in demo mode - Stripe API key not configured")
    
    def get_pricing_plans(self) -> List[PricingPlan]:
        """Get all available pricing plans."""
        return list(PRICING_PLANS.values())
    
    def get_plan(self, plan_id: str) -> Optional[PricingPlan]:
        """Get a specific pricing plan."""
        return PRICING_PLANS.get(plan_id)
    
    async def create_checkout_session(
        self,
        request: CreateCheckoutRequest
    ) -> CheckoutSessionResponse:
        """
        Create a Stripe checkout session.
        
        Args:
            request: Checkout request with plan and customer details
            
        Returns:
            CheckoutSessionResponse with session URL
        """
        plan = self.get_plan(request.plan_id)
        if not plan:
            raise ValueError(f"Invalid plan: {request.plan_id}")
        
        # Determine price based on billing period
        if request.billing_period == "yearly":
            amount = int(plan.price_yearly * 100)  # Cents
            interval = "year"
        else:
            amount = int(plan.price_monthly * 100)
            interval = "month"
        
        # If Stripe is configured, create real session
        if self._stripe:
            try:
                session = self._stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    line_items=[{
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": f"ASL Biometric - {plan.name} Plan",
                                "description": ", ".join(plan.features[:3]),
                            },
                            "unit_amount": amount,
                            "recurring": {"interval": interval}
                        },
                        "quantity": 1
                    }],
                    mode="subscription",
                    success_url=request.success_url,
                    cancel_url=request.cancel_url,
                    customer_email=request.customer_email,
                    metadata={
                        "plan_id": request.plan_id,
                        "billing_period": request.billing_period,
                        **request.metadata
                    }
                )
                
                return CheckoutSessionResponse(
                    session_id=session.id,
                    url=session.url,
                    expires_at=datetime.fromtimestamp(session.expires_at).isoformat()
                )
                
            except Exception as e:
                logger.error(f"Stripe checkout error: {str(e)}")
                raise
        
        # Demo mode - return mock session
        demo_session_id = f"cs_demo_{datetime.utcnow().timestamp()}"
        return CheckoutSessionResponse(
            session_id=demo_session_id,
            url=f"/demo/checkout/{demo_session_id}?plan={request.plan_id}",
            expires_at=datetime.utcnow().isoformat()
        )
    
    async def create_portal_session(
        self,
        customer_id: str,
        return_url: str
    ) -> PortalSessionResponse:
        """
        Create a Stripe customer portal session.
        
        Args:
            customer_id: Stripe customer ID
            return_url: URL to return to after portal
            
        Returns:
            PortalSessionResponse with portal URL
        """
        if self._stripe:
            try:
                session = self._stripe.billing_portal.Session.create(
                    customer=customer_id,
                    return_url=return_url
                )
                
                return PortalSessionResponse(
                    url=session.url,
                    return_url=return_url
                )
                
            except Exception as e:
                logger.error(f"Portal session error: {str(e)}")
                raise
        
        # Demo mode
        return PortalSessionResponse(
            url=f"/demo/portal/{customer_id}",
            return_url=return_url
        )
    
    async def handle_webhook(
        self,
        payload: bytes,
        signature: str
    ) -> Dict[str, Any]:
        """
        Handle Stripe webhook events.
        
        Args:
            payload: Raw webhook payload
            signature: Stripe signature header
            
        Returns:
            Processing result
        """
        if not self._stripe:
            return {"status": "demo_mode", "message": "Webhook received in demo mode"}
        
        try:
            event = self._stripe.Webhook.construct_event(
                payload,
                signature,
                self.stripe_webhook_secret
            )
            
            # Handle different event types
            if event.type == "checkout.session.completed":
                await self._handle_checkout_completed(event.data.object)
            elif event.type == "customer.subscription.updated":
                await self._handle_subscription_updated(event.data.object)
            elif event.type == "customer.subscription.deleted":
                await self._handle_subscription_deleted(event.data.object)
            elif event.type == "invoice.payment_succeeded":
                await self._handle_payment_succeeded(event.data.object)
            elif event.type == "invoice.payment_failed":
                await self._handle_payment_failed(event.data.object)
            
            return {"status": "success", "event_type": event.type}
            
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            raise
    
    async def _handle_checkout_completed(self, session: Dict[str, Any]) -> None:
        """Handle checkout.session.completed event."""
        subscription_id = session.get("subscription")
        customer_id = session.get("customer")
        metadata = session.get("metadata", {})
        
        logger.info(f"Checkout completed: subscription={subscription_id}")
        
        # Create subscription record
        plan = self.get_plan(metadata.get("plan_id", "starter"))
        if plan:
            self.subscriptions[subscription_id] = SubscriptionInfo(
                subscription_id=subscription_id,
                customer_id=customer_id,
                plan_id=plan.id,
                status=SubscriptionStatus.ACTIVE,
                current_period_start=datetime.utcnow().isoformat(),
                current_period_end=datetime.utcnow().isoformat(),
                verifications_remaining=plan.verifications_included
            )
    
    async def _handle_subscription_updated(self, subscription: Dict[str, Any]) -> None:
        """Handle customer.subscription.updated event."""
        subscription_id = subscription.get("id")
        status = subscription.get("status")
        
        logger.info(f"Subscription updated: {subscription_id} -> {status}")
        
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id].status = SubscriptionStatus(status)
    
    async def _handle_subscription_deleted(self, subscription: Dict[str, Any]) -> None:
        """Handle customer.subscription.deleted event."""
        subscription_id = subscription.get("id")
        
        logger.info(f"Subscription deleted: {subscription_id}")
        
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id].status = SubscriptionStatus.CANCELED
    
    async def _handle_payment_succeeded(self, invoice: Dict[str, Any]) -> None:
        """Handle invoice.payment_succeeded event."""
        subscription_id = invoice.get("subscription")
        
        logger.info(f"Payment succeeded for subscription: {subscription_id}")
        
        # Reset verification count for new billing period
        if subscription_id in self.subscriptions:
            sub = self.subscriptions[subscription_id]
            plan = self.get_plan(sub.plan_id)
            if plan:
                sub.verifications_remaining = plan.verifications_included
                sub.current_period_start = datetime.utcnow().isoformat()
    
    async def _handle_payment_failed(self, invoice: Dict[str, Any]) -> None:
        """Handle invoice.payment_failed event."""
        subscription_id = invoice.get("subscription")
        
        logger.warning(f"Payment failed for subscription: {subscription_id}")
        
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id].status = SubscriptionStatus.PAST_DUE
    
    def get_subscription(self, subscription_id: str) -> Optional[SubscriptionInfo]:
        """Get subscription information."""
        return self.subscriptions.get(subscription_id)
    
    def record_verification_usage(
        self,
        subscription_id: str,
        use_case: str
    ) -> Dict[str, Any]:
        """
        Record a verification usage.
        
        Args:
            subscription_id: Subscription ID
            use_case: Type of verification use case
            
        Returns:
            Usage update result
        """
        sub = self.subscriptions.get(subscription_id)
        if not sub:
            return {"error": "Subscription not found"}
        
        plan = self.get_plan(sub.plan_id)
        if not plan:
            return {"error": "Plan not found"}
        
        # Update usage
        sub.verifications_used = sub.verifications_used + 1
        sub.verifications_remaining = max(0, sub.verifications_remaining - 1)
        
        # Track by use case
        if subscription_id not in self.usage:
            self.usage[subscription_id] = UsageReport(
                subscription_id=subscription_id,
                period_start=sub.current_period_start,
                period_end=sub.current_period_end,
                verifications_included=plan.verifications_included,
                verifications_used=0,
                breakdown_by_use_case={}
            )
        
        usage = self.usage[subscription_id]
        usage.verifications_used += 1
        usage.breakdown_by_use_case[use_case] = \
            usage.breakdown_by_use_case.get(use_case, 0) + 1
        
        # Calculate overage
        if usage.verifications_used > usage.verifications_included:
            usage.overage_count = usage.verifications_used - usage.verifications_included
            usage.overage_cost = usage.overage_count * plan.overage_cost
        
        return {
            "success": True,
            "verifications_used": sub.verifications_used,
            "verifications_remaining": sub.verifications_remaining,
            "overage": usage.overage_count > 0
        }
    
    def get_usage_report(self, subscription_id: str) -> Optional[UsageReport]:
        """Get usage report for a subscription."""
        return self.usage.get(subscription_id)


# Global instance
stripe_service = StripeSubscriptionService()
