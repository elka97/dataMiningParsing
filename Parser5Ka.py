"""Источник: https://5ka.ru/special_offers/
Задача организовать сбор данных, необходимо иметь метод сохранения данных в .json файлы
результат: Данные скачиваются с источника, при вызове метода/функции сохранения в файл скачанные данные сохраняются в Json fайлы,
для каждой категории товаров должен быть создан отдельный файл и содержать товары исключительно соответсвующие данной категории.
пример структуры данных для файла:
нейминг ключей можно делать отличным от примера
{
"name": "имя категории",
"code": "Код соответсвующий категории (используется в запросах)",
"products": [{PRODUCT}, {PRODUCT}........] # список словарей товаров соответсвующих данной категории
}
Инструкция к сдаче
Настоятельно рекомендуем сдавать практическое задание в виде ссылки на pull request.
Рекомендуемый способ организации данных в репозитории: создать отдельные папки по темам и помещать в них отдельные файлы для каждой задачи с правильным расширением.
"""
import time
import json
from pathlib import Path
import requests as requests


class GetResponse:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
    }

    def __init__(self, delay=0.9):
        self.delay = delay

    def get_response(self, p_url, params=None):
        while True:
            if params is not None:
                response = requests.get(p_url, params=params, headers=self.headers)
            else:
                response = requests.get(p_url, headers=self.headers)
            if response.status_code == 200:
                return response
            time.sleep(self.delay)


class Parser5Ka(GetResponse):

    def __init__(self, base_url, shop, save_path: Path, delay=0.9):
        super(Parser5Ka, self).__init__(delay)
        self.base_url = base_url
        self.save_path = save_path
        self.shop = shop
        self.records_per_page = 200

    def offers_categories(self, start_url):
        categories_response = super().get_response(p_url=f"{self.base_url}{start_url}")
        categories_list: dict = categories_response.json()
        for cat in categories_list:
            file_path = self.save_path.joinpath(f"{cat['parent_group_code']}.json")
            try:
                data = {"name": cat['parent_group_name'],
                        "code": cat['parent_group_code'],
                        "products": []}
                url = f"{self.base_url}special_offers/?categories={cat['parent_group_code']}&ordering=&page=1&price_promo__gte=&price_promo__lte=&records_per_page={self.records_per_page}&search=&store={self.shop}"
                for products in self._next_cat_page(url):
                    data["products"].append(products)
                self._save(data, file_path)
            except Exception as e:
                print("Exception occurred: ", e)

    def _next_cat_page(self, url):
        while url:
            response = super().get_response(p_url=url)
            data: dict = response.json()
            url = data["next"]
            for products in data['results']:
                yield products

    def _save(self, data: dict, file_path: Path):
        file_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def get_save_path(dir_name: str) -> Path:
    save_path = Path(__file__).parent.parent.joinpath(dir_name)
    if not save_path.exists():
        save_path.mkdir()
    return save_path


if __name__ == "__main__":
    category_product_path = get_save_path('5ka_category_product')
    parser = Parser5Ka(base_url="https://5ka.ru/api/v2/", shop="363H", save_path=category_product_path, delay=0.1)
    parser.offers_categories(start_url="categories/")
