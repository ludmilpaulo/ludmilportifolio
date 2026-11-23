from django.core.management.base import BaseCommand

from information.models import Project

# Keyed by public slug. problem: what is hard today. description: the solution on cards and in share text.
COPY = {
    "vendora": (
        "Shops split the till, the stock list, and the staff roster across different tools.",
        "Vendora puts sales, stock, staff, and billing in one place for every shop.",
    ),
    "rubiane_joaquim_educação_financeira": (
        "Learners look for money skills in scattered videos and never see what they finished.",
        "Zenda opens paid courses, mentoring, and a learner's progress in one app.",
    ),
    "mzansi_visa_solutions": (
        "Visa cases get lost across email and files. Mzansi Visa does not grant visas.",
        "Mzansi Visa keeps each case, its documents, and the staff updates in one place.",
    ),
    "maindo_digital_agency": (
        "A business and its agency lose the thread between the public site and the work.",
        "Maindo is the agency site where clients see the work and stay in one conversation.",
    ),
    "indaba": (
        "Local stories are scattered, and tips can publish before an editor checks them.",
        "Indaba & Meer is news, short video, and tips an editor checks before they go live.",
    ),
    "fleet360": (
        "Fleet teams track vehicles, drivers, maintenance, and compliance in separate sheets.",
        "Fleet360 is one desk for vehicles, drivers, maintenance, and compliance.",
    ),
    "fit_app": (
        "A training plan is easy to drop when the next workout is hard to find.",
        "Fit App lets someone browse workouts and follow a session from their phone.",
    ),
    "cape_town_basketball_association": (
        "Clubs, referees, parents, and officials each keep a different fixture list.",
        "CTBA is the home for clubs, fixtures, results, and the people around a match.",
    ),
    "brightfuture": (
        "Learners miss mentors and scholarships because the options are scattered.",
        "BrightFuture matches learners with mentors and scholarships and records progress.",
    ),
    "legalease": (
        "Everyday legal steps are hard to follow when a lawyer is out of reach.",
        "LegalEase walks someone through tenancy, a new business, and simple contracts.",
    ),
    "foodrescue": (
        "Surplus food is thrown away while shelters are still looking for meals.",
        "FoodRescue links restaurants and grocers with shelters and tracks the pickup.",
    ),
    "joblift": (
        "Job seekers and small businesses rarely find each other in the same place.",
        "JobLift lets a small business post a role and match it to people by skill.",
    ),
    "artisanhub": (
        "Local makers struggle to show their stock and reach buyers past their street.",
        "ArtisanHub is a shop where makers list products and sell to new customers.",
    ),
    "safejourney": (
        "A passenger in trouble on public transport cannot quickly show where they are.",
        "SafeJourney shares a live location with trusted contacts and asks for help.",
    ),
    "cleancity": (
        "Dumped waste stays invisible when the report never reaches the city.",
        "CleanCity lets residents report dumping and broken services, then shows the response.",
    ),
    "agrismart": (
        "Small farms guess at soil, crops, and weather without the instruments.",
        "AgriSmart turns soil, crop, and weather readings into advice a farm can use.",
    ),
    "healthmate": (
        "Rural patients travel for a visit and have no single record of their care.",
        "HealthMate lets a patient book a doctor and keep their medical history together.",
    ),
    "edubridge": (
        "Students without a nearby tutor also miss scholarships they could apply for.",
        "EduBridge pairs students with remote mentors and keeps lessons and scholarships.",
    ),
    "video_slider_project": (
        "A long page of videos makes people hunt for the next story.",
        "This video slider lets a visitor move through films and still reach contact links.",
    ),
    "the-movie-database-api": (
        "Film fans jump between sites to find a movie and remember what they liked.",
        "This app lists films, saves favourites, and keeps that list behind a sign-in.",
    ),
    "kudya:_a_comprehensive_food_delivery_solution": (
        "A food order splits into separate chats for the customer, restaurant, and driver.",
        "Kudya lets a customer order nearby, and the restaurant and driver finish that order.",
    ),
}


class Command(BaseCommand):
    help = "Set each project description to the problem its app solves."

    def handle(self, *args, **options):
        updated = 0
        for slug, (problem, solution) in COPY.items():
            changed = Project.objects.filter(slug=slug).update(problem=problem, description=solution)
            if changed:
                updated += changed
                self.stdout.write(f"{slug}: {solution}")
            else:
                self.stderr.write(f"Missing project {slug}")
        self.stdout.write(self.style.SUCCESS(f"Updated {updated} projects."))
