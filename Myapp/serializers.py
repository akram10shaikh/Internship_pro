from rest_framework import serializers
from .models import CustomUser, StripePayment

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'full_name', 'phone_number', 
            'website_name', 'linkedin_url', 'no_linkedin', 'paid'
            'email_verified', 'is_active', 'last_login'
        ]
        read_only_fields = ['id', 'email', 'email_verified', 'is_active', 'date_joined', 'last_login']
    
    def validate_phone_number(self, value):
        """
        Validate phone number format
        """
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits long.")
        return value
    
    def validate_full_name(self, value):
        """
        Validate full name
        """
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Full name must be at least 2 characters long.")
        return value.strip()
    
    def validate_website_name(self, value):
        """
        Validate website/company name
        """
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError("Company name must be at least 2 characters long.")
        return value.strip() if value else value

class StripePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StripePayment
        fields = ['id', 'user', 'email', 'amount', 'currency', 'status', 'created_at']

from rest_framework import serializers
from .models import StripePayment

class StripePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StripePayment
        fields = [
            'id', 'stripe_session_id', 'stripe_payment_intent_id', 
            'email', 'amount', 'currency', 'status', 'customer_name', 
            'company_name', 'product_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Format dates for better frontend consumption
        if data.get('created_at'):
            data['created_at'] = instance.created_at.strftime('%Y-%m-%d %H:%M:%S')
        if data.get('updated_at'):
            data['updated_at'] = instance.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        return data


class UserOverviewSerializer(serializers.ModelSerializer):
    current_plan = serializers.SerializerMethodField()
    registration_date = serializers.DateTimeField(source='date_joined', format="%Y-%m-%d", required=False)
    upgrade_date = serializers.SerializerMethodField()
    tag = serializers.SerializerMethodField()
    payment_id = serializers.SerializerMethodField()
    payment_date = serializers.SerializerMethodField()
    payment_amount = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'full_name', 'username', 'email', 'phone_number', 'role',
            'current_plan', 'registration_date', 'upgrade_date', 'tag',
            'payment_id', 'payment_date', 'payment_amount',
        ]

    def get_current_plan(self, obj):
        try:
            return obj.usersubscription.plan.name
        except Exception:
            return None

    def get_upgrade_date(self, obj):
        try:
            return obj.usersubscription.updated_at
        except Exception:
            return None

    def get_tag(self, obj):
        # Example: Plan name as tag (customize as needed)
        try:
            return obj.usersubscription.plan.name
        except Exception:
            return None

    def get_payment_id(self, obj):
        last_payment = StripePayment.objects.filter(user=obj, status__in=['completed', 'succeeded']).order_by('-created_at').first()
        return last_payment.stripe_payment_intent_id if last_payment else None

    def get_payment_date(self, obj):
        last_payment = StripePayment.objects.filter(user=obj, status__in=['completed', 'succeeded']).order_by('-created_at').first()
        return last_payment.created_at if last_payment else None

    def get_payment_amount(self, obj):
        last_payment = StripePayment.objects.filter(user=obj, status__in=['completed', 'succeeded']).order_by('-created_at').first()
        return last_payment.amount if last_payment else None