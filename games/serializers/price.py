from rest_framework import serializers

from ..models import SwitchGamePrice, SwitchGameSale


class SwitchGamePriceSerializer(serializers.Serializer):
    amount = serializers.CharField(max_length=12)
    currency = serializers.CharField(max_length=8)
    raw_value = serializers.CharField(max_length=10)


    def create(self, validated_data):
        price = SwitchGamePrice(
            game=self.context['game'],
            country=self.context['country'],

            amount=validated_data['amount'],
            currency=validated_data['currency'],
            raw_value=float(validated_data['raw_value']),
        )

        price.save()
        return price

    def update(self, instance, validated_data):
        instance.amount = validated_data['amount']
        instance.currency = validated_data['currency']
        instance.raw_value = float(validated_data['raw_value'])

        instance.save()
        return instance


class SwitchGameSaleSerializer(serializers.Serializer):
    amount = serializers.CharField(max_length=12)
    currency = serializers.CharField(max_length=8)
    raw_value = serializers.CharField(max_length=10)

    start_datetime = serializers.DateTimeField(required=False)
    end_datetime = serializers.DateTimeField(required=False)

    def create(self, validated_data):
        price = SwitchGameSale(
            game=self.context['game'],
            country=self.context['country'],

            amount=validated_data['amount'],
            currency=validated_data['currency'],
            raw_value=float(validated_data['raw_value']),

            start_datetime=validated_data['start_datetime'],
            end_datetime=validated_data['end_datetime'],
        )

        price.save()
        return price

    def update(self, instance, validated_data):
        instance.amount = validated_data['amount']
        instance.currency = validated_data['currency']
        instance.raw_value = float(validated_data['raw_value'])

        start_datetime = validated_data['start_datetime']
        end_datetime = validated_data['end_datetime']

        instance.save()
        return instance
