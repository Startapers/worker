
import json
import spacy
from utils import dismiss_mutually_exclusive, get_most_similar, \
    get_simmilarity_marix, sort_by_simmilarity_value, summarize_coef


class RecommendationGenerator:
    def __init__(self, cache_dal, user_dal) -> None:
        self.cache_dal = cache_dal
        self.user_dal = user_dal

    async def generate_recommendations_for_new(self, user_id, tags):
        try:
            #get similar categories
            if (not len(tags)):
                return

            online_tag = tags.pop()

            categories = await self.user_dal.get_categories_based_on_labels(tags, [])

            categories = self.user_dal.get_online_lessons_by_overall_percentage_in_categories(categories, online_tag)

            recommendation_ids = [categry.get('id') for categry in categories]

            constraints = await self.user_dal.check_constarint_tags(recommendation_ids)

            if len(constraints):
                recommendation_ids.extend(constraints)

            print("Saved for new user: ", user_id)

            await self.cache_dal.set('worker:recommend:{}'.format(user_id), json.dumps(recommendation_ids))
        except Exception as e:
            print(e)

    async def generate_recommendatations(self, user_id):
        try:
            #get visits
            visits = await self.user_dal.get_user_visits_by_id(user_id)
            tags = []
            ids_to_exclude = []

            if (not len(visits)):
                return

            for visit in visits:
                [tags.append(desc) for desc in visit.get('tags')]
                ids_to_exclude.append(visit.get('category_id'))

            if (not len(visits)):
                return

            tags = list(set(tags))

            #get similar categories
            categories = await self.user_dal.get_categories_based_on_labels(tags, ids_to_exclude)

            if (not len(categories)):
                return

            matrix = get_simmilarity_marix(visits, categories)
            simmilars = get_most_similar(matrix)
            sort_by_simmilarity_value(simmilars)

            filtered = dismiss_mutually_exclusive(simmilars)
            filtered = summarize_coef(filtered)
            filtered.sort(key=lambda x: x[1], reverse=True)

            recommendation_ids = [el[0] for el in filtered]

            constraints = await self.user_dal.check_constarint_tags(recommendation_ids)

            if len(constraints):
                recommendation_ids.extend(constraints)

            print("Saved: ", user_id)

            await self.cache_dal.set('worker:recommend:{}'.format(user_id), json.dumps(recommendation_ids))
        except Exception as e:
            print(e)

    async def run_model(self):
        # add tags 
        nlp = spacy.load('./output/gen_all_3')
        res = await self.user_dal.get_all_descriptions_and_lvl_3_ids()
        for descr in res:
            id = descr.get('id')
            text = descr.get('description')
            doc = nlp(text)
            tags = []
            for ent in doc.ents:
                tags.append("{}".format(ent.label_))
            await self.user_dal.save_tags(id, tags)

    async def generate_all(self):
        cursor = await self.user_dal.get_all_users_cursor()
        while True:
            row = cursor.fetchone()
            if not row:
                break

            id = row.get('id')
            await self.generate_recommendatations(id)

        cursor.close()
        print(cursor)
