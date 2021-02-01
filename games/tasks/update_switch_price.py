from celery import shared_task

from games.models import (
    SwitchGame,
    SwitchGameUS,
    SwitchGameEU,
    SwitchGamePrice,
    SwitchGameSale,
)

from games.tasks.update_utils import treated_request

from games.serializers import (
    SwitchGamePriceSerializer,
    SwitchGameSaleSerializer,
)


@shared_task()
def update_switch_price():
    print('Updating Switch games\' prices...')

    # Prices in the America region
    for country in ['US', 'CA', 'MX']: # , 'AR', 'BR', 'CL']:
        update_country(country, SwitchGameUS)

    # Prices in the Europe region
    for country in ['GB', 'DE', 'FR', 'ZA', 'RU']:
        update_country(country, SwitchGameEU)

    print('Finished updating Switch games\' prices.')


def update_country(country, model):
    url = 'https://api.ec.nintendo.com/v1/price'
    count = model.objects.count()

    found_price = 0
    found_sales = 0

    for offset in range(0, count, 50):
        print('Updating {}\'s price offset {}'.format(country, offset))

        games = model.objects.all()[offset:offset+50].values('nsuid')
        games = list(map(lambda game: game['nsuid'], games))
        games = ','.join([nsuid for nsuid in games if nsuid != None])

        params = {'lang': 'en', 'country': country, 'ids': games}
        req = treated_request(url, params, 'US Switch price')

        data = req.json()['prices']

        for price_info in data:
            if model.objects.filter(nsuid=price_info['title_id']).count() > 1:
                print('Multiple games found for nsuid {}'.format(price_info['title_id']))

            game = model.objects.filter(nsuid=price_info['title_id'])[0]

            if 'regular_price' in price_info:
                found_price = found_price + 1

                if SwitchGamePrice.objects.filter(game=game.switchgame,
                                                  country=country).exists():
                    price = SwitchGamePrice.objects.get(
                        game=game.switchgame, country=country)

                    serialized = SwitchGamePriceSerializer(
                        data=price_info['regular_price'],
                        context={'game': game.switchgame, 'country': country},
                        instance=price)
                else:
                    serialized = SwitchGamePriceSerializer(
                        data=price_info['regular_price'],
                        context={'game': game.switchgame, 'country': country})

                if serialized.is_valid():
                    serialized.save()

            if 'discount_price' in price_info:
                found_sales = found_sales + 1

                if SwitchGameSale.objects.filter(game=game.switchgame,
                                                 country=country).exists():
                    price = SwitchGameSale.objects.get(
                        game=game.switchgame, country=country)

                    serialized = SwitchGameSaleSerializer(
                        data=price_info['discount_price'],
                        instance=price,
                        context={'game': game.switchgame, 'country': country})
                else:
                    serialized = SwitchGameSaleSerializer(
                        data=price_info['discount_price'],
                        context={'game': game.switchgame, 'country': country})

                if serialized.is_valid():
                    serialized.save()

            else:
                SwitchGameSale.objects \
                    .filter(game=game.switchgame, country=country).delete()

    print('Found {} prices and {} sales for country {}'
        .format(found_price, found_sales, country))
