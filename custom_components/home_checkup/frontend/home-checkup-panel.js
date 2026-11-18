// Home Checkup: the page in the Home Assistant sidebar (admins only).
// One small file with no outside parts. It reads the report and changes only Home Checkup's own "Keep" list.
// It never changes the home.

const WORDS = {
  en: {},
  fr: {
    "Home Checkup": "Bilan de la maison",
    "Home is healthy": "La maison va bien",
    "{n} thing needs a look": "{n} point à vérifier",
    "{n} things need a look": "{n} points à vérifier",
    "Nothing changes until you choose to.": "Rien ne change sans votre accord.",
    "Nothing needs a look today.": "Rien à vérifier aujourd’hui.",
    "Checked {time}": "Vérifié à {time}",
    "Not checked yet": "Pas encore vérifié",
    "Check now": "Vérifier",
    "Checking…": "Vérification…",
    "Good to know": "Bon à savoir",
    "Integrations": "Intégrations",
    "Log": "Journal",
    "Automations": "Automatisations",
    "Leftovers": "Restes",
    "Offline": "Hors ligne",
    "Helpers": "Entrées",
    "{n} integration did not start": "{n} intégration n’a pas démarré",
    "{n} integrations did not start": "{n} intégrations n’ont pas démarré",
    "Errors from {name}": "Erreurs de {name}",
    "Warnings from {name}": "Avertissements de {name}",
    "{n} broken automation step": "{n} étape d’automatisation cassée",
    "{n} broken automation steps": "{n} étapes d’automatisation cassées",
    "{n} leftover entity": "{n} entité orpheline",
    "{n} leftover entities": "{n} entités orphelines",
    "{n} leftover device": "{n} appareil orphelin",
    "{n} leftover devices": "{n} appareils orphelins",
    "{n} entity offline for a long time": "{n} entité hors ligne depuis longtemps",
    "{n} entities offline for a long time": "{n} entités hors ligne depuis longtemps",
    "{n} helper nothing seems to use": "{n} entrée que rien ne semble utiliser",
    "{n} helpers nothing seems to use": "{n} entrées que rien ne semble utiliser",
    "Their devices do not work until they start again.": "Leurs appareils ne marchent pas tant qu’elles ne redémarrent pas.",
    "Grouped by cause, last 24 hours.": "Regroupées par cause, dernières 24 heures.",
    "Usually harmless. Shown, not counted.": "Souvent sans gravité. Affichés, non comptés.",
    "These steps will fail when they run.": "Ces étapes échoueront à leur exécution.",
    "Nothing provides them any more.": "Plus rien ne les fournit.",
    "Their integration is gone.": "Leur intégration a été supprimée.",
    "Off, unplugged or out of range.": "Éteints, débranchés ou hors de portée.",
    "Shown, not counted. Something outside may still use them.": "Affichées, non comptées. Un outil externe peut encore s’en servir.",
    "a removed device": "un appareil supprimé",
    "Open": "Ouvrir",
    "Ignore": "Ignorer",
    "Ignore means this is fine. It will not show again.": "Ignorer veut dire que c’est normal. Cela ne s’affichera plus.",
    "Show all {n}": "Tout afficher ({n})",
    "Show fewer": "Afficher moins",
    "Show the full error": "Afficher l’erreur complète",
    "Show all lines": "Afficher toutes les lignes",
    "Copy": "Copier",
    "Copied": "Copié",
    "First seen {when}": "Vue pour la première fois : {when}",
    "{n} integrations checked. All started.": "{n} intégrations vérifiées. Toutes ont démarré.",
    "The log of the last 24 hours was read. No error keeps coming back.": "Le journal des dernières 24 heures a été lu. Aucune erreur ne revient.",
    "{n} automations and scripts checked. No broken steps.": "{n} automatisations et scripts vérifiés. Aucune étape cassée.",
    "{n} entities and {m} devices checked. No leftovers.": "{n} entités et {m} appareils vérifiés. Aucun reste.",
    "{n} entities checked. None was offline for a long time.": "{n} entités vérifiées. Aucune n’est restée hors ligne longtemps.",
    "{n} helpers checked. All are in use.": "{n} entrées vérifiées. Toutes sont utilisées.",
    "{n} batteries checked. None is low.": "{n} piles vérifiées. Aucune n’est faible.",
    "Helpers are checked with the next full check.": "Les entrées sont vérifiées au prochain contrôle complet.",
    "Likely from {name}": "Vient sans doute de {name}",
    "Last seen {when}": "Vue pour la dernière fois : {when}",
    "{n} times in 24 hours": "{n} fois en 24 heures",
    "Known issues": "Problèmes connus",
    "Debug logging": "Journal de débogage",
    "The integration page has the debug logging switch.": "La page de l’intégration contient l’interrupteur du journal de débogage.",
    "Copies a report you can paste into a bug report.": "Copie un rapport à coller dans un signalement de bogue.",
    "Could not read the full error.": "Impossible de lire l’erreur complète.",
    "Ignored. It will not show again.": "Ignoré. Cela ne s’affichera plus.",
    "Undo": "Annuler",
    "Ignored items ({n})": "Éléments ignorés ({n})",
    "Show again": "Afficher de nouveau",
    "Home Checkup only reads. It never changes, removes or restarts anything by itself.": "Le bilan ne fait que lire. Il ne change, ne supprime et ne redémarre rien par lui-même.",
    "Home Checkup is not set up.": "Le bilan de la maison n’est pas configuré.",
    "Add it in Settings, Devices and services.": "Ajoutez-le dans Paramètres, Appareils et services.",
    "Could not load the report.": "Impossible de charger le rapport.",
    "Remove…": "Retirer…",
    "Remove leftover entities": "Retirer les entités orphelines",
    "Remove helpers nothing uses": "Retirer les entrées inutilisées",
    "Nothing provides these any more. Untick any you want to keep.": "Plus rien ne les fournit. Décochez celles que vous voulez garder.",
    "Pick only the ones you are sure about. Something outside Home Assistant, like Node-RED, may still use them.": "Choisissez seulement celles dont vous êtes sûr. Un outil hors de Home Assistant, comme Node-RED, peut encore s’en servir.",
    "A backup is made first. You can undo this for 30 days.": "Une sauvegarde est faite d’abord. Vous pouvez annuler pendant 30 jours.",
    "Tick all": "Tout cocher",
    "Untick all": "Tout décocher",
    "Made in YAML. Remove it from your YAML files.": "Créée en YAML. Retirez-la de vos fichiers YAML.",
    "Nothing to remove.": "Rien à retirer.",
    "Cancel": "Annuler",
    "Removing…": "Retrait…",
    "Remove {n}": "Retirer {n}",
    "Remove": "Retirer",
    "Removed {n}. A backup was made.": "{n} retiré(s). Une sauvegarde a été faite.",
    "Removed {n} of {m}. Some did not change. You can undo it.": "{n} sur {m} retiré(s). Certains n’ont pas changé. Vous pouvez annuler.",
    "Undone. {n} brought back.": "Annulé. {n} rétabli(s).",
    "Something went wrong. Nothing was changed.": "Un problème est survenu. Rien n’a changé.",
    "Something went wrong.": "Un problème est survenu.",
    "Recent fixes": "Corrections récentes",
    "Removed {n} leftover entity": "{n} entité orpheline retirée",
    "Removed {n} leftover entities": "{n} entités orphelines retirées",
    "Removed {n} helper": "{n} entrée retirée",
    "Removed {n} helpers": "{n} entrées retirées",
    "Undone": "Annulé",
    "Some did not change": "Certains n’ont pas changé",
    "Home Checkup never changes anything by itself. A fix happens only when you tap it.": "Le bilan ne change rien par lui-même. Une correction se fait seulement quand vous la touchez.",
    "Something points to an entity that no longer exists.": "Quelque chose pointe vers une entité qui n’existe plus.",
    "It starts slowly. Usually harmless.": "Il démarre lentement. Souvent sans gravité.",
    "Try: {text}": "À essayer : {text}",
    "A dashboard card had a fault in the browser.": "Une carte du tableau de bord a eu un défaut dans le navigateur.",
    "Update that card, then reload the page.": "Mettez cette carte à jour, puis rechargez la page.",
    "It did not answer in time.": "Pas de réponse à temps.",
    "Check that it is on and close to Wi-Fi.": "Vérifiez qu’il est allumé et proche du Wi-Fi.",
    "Home Assistant could not reach it.": "Home Assistant n’a pas pu le joindre.",
    "Check that it is on and on the network.": "Vérifiez qu’il est allumé et sur le réseau.",
    "Its sign-in no longer works.": "Sa connexion ne fonctionne plus.",
    "Open the integration and sign in again.": "Ouvrez l’intégration et connectez-vous à nouveau.",
    "The service asked Home Assistant to slow down.": "Le service a demandé à Home Assistant de ralentir.",
    "Wait. This usually fixes itself.": "Attendez. Cela se règle souvent tout seul.",
    "A secure connection failed.": "Une connexion sécurisée a échoué.",
    "Check the address and the certificate.": "Vérifiez l’adresse et le certificat.",
    "It was asked to start something that was already running. Usually harmless.": "On lui a demandé de démarrer quelque chose qui tournait déjà. Souvent sans gravité.",
    "The storage is full.": "Le stockage est plein.",
    "Free some space, for example old backups.": "Libérez de la place, par exemple d’anciennes sauvegardes.",
    "Home Assistant ran out of memory.": "Home Assistant a manqué de mémoire.",
    "Restart Home Assistant.": "Redémarrez Home Assistant.",
    "Home Assistant is not allowed to open a file.": "Home Assistant n’a pas le droit d’ouvrir un fichier.",
    "Check the permissions of that file.": "Vérifiez les droits de ce fichier.",
    "An address could not be found.": "Une adresse est introuvable.",
    "Check the internet connection.": "Vérifiez la connexion Internet.",
    "The connection dropped. It usually comes back by itself.": "La connexion a été coupée. Elle revient souvent toute seule.",
    "The device is offline.": "L’appareil est hors ligne.",
    "Check its power and Wi-Fi.": "Vérifiez son alimentation et le Wi-Fi.",
    "The service itself had a problem.": "Le service lui-même a eu un problème.",
    "Something calls an action that does not exist.": "Quelque chose appelle une action qui n’existe pas.",
    "Check your automations and cards.": "Vérifiez vos automatisations et vos cartes.",
    "It asked for something that does not exist.": "Il a demandé quelque chose qui n’existe pas.",
    "Update the integration.": "Mettez l’intégration à jour.",
    "The integration works in a way Home Assistant warns about.": "L’intégration travaille d’une façon que Home Assistant signale.",
    "It uses something Home Assistant will remove.": "Il utilise quelque chose que Home Assistant va retirer.",
    "A template reads something that is missing.": "Un modèle lit quelque chose qui manque.",
    "Check the template.": "Vérifiez le modèle.",
    "Something points to an entity that no longer exists.": "Quelque chose pointe vers une entité qui n’existe plus.",
    "Change it to an entity that exists.": "Remplacez-la par une entité qui existe.",
    "The device cannot do what was asked.": "L’appareil ne peut pas faire ce qui a été demandé.",
    "Check the automation or card that asked for it.": "Vérifiez l’automatisation ou la carte qui l’a demandé.",
    "It got an answer it could not read.": "Il a reçu une réponse qu’il n’a pas pu lire.",
    "It got a value it cannot use.": "Il a reçu une valeur qu’il ne peut pas utiliser.",
    "Check the automation or card that sent it.": "Vérifiez l’automatisation ou la carte qui l’a envoyée.",
    "This is a fault in its code.": "C’est un défaut dans son code.",
    "Update it. If the error stays, report it to its makers.": "Mettez-le à jour. Si l’erreur reste, signalez-la à ses auteurs.",
    "The history database had a problem. Your history may have a gap.": "La base d’historique a eu un problème. Votre historique peut avoir un trou.",
    "Batteries": "Piles",
    "{n} battery running low": "{n} pile presque vide",
    "{n} batteries running low": "{n} piles presque vides",
    "Change them before the device stops working.": "Changez-les avant que l’appareil s’arrête.",
    "New": "Nouveau",
    "Renamed to {name}": "Renommé en {name}",
    "{name} was removed": "{name} a été supprimé",
    "Its device was removed": "Son appareil a été supprimé",
    "No longer exists": "N’existe plus",
    "Use the new one": "Utiliser le nouveau",
    "Choose another": "Choisir un autre",
    "Choose what this step should use": "Choisissez ce que cette étape doit utiliser",
    "{name} points to {old}, which no longer exists. Choose what it should use now. A backup is made first.": "{name} pointe vers {old}, qui n’existe plus. Choisissez ce qu’elle doit utiliser maintenant. Une sauvegarde est faite d’abord.",
    "Search": "Rechercher",
    "Nothing of the same kind was found.": "Rien du même type n’a été trouvé.",
    "Written in {file}, line {line}. Change it in that file.": "Écrit dans {file}, ligne {line}. Modifiez-le dans ce fichier.",
    "This script lives in a YAML file. Open it to change it.": "Ce script se trouve dans un fichier YAML. Ouvrez-le pour le modifier.",
    "Showing the first {n}. Search to find more.": "Les {n} premiers sont affichés. Recherchez pour en trouver d’autres.",
    "Ask": "Demander",
    "Ask sends us a request for a fix. You read it first.": "Demander nous envoie une demande de correctif. Vous la lisez d’abord.",
    "Ask for a fix": "Demander un correctif",
    "Asked": "Demandé",
    "A fix arrived in version {version}. Update to get it.": "Un correctif est arrivé dans la version {version}. Mettez à jour pour l’obtenir.",
    "A fix arrived.": "Un correctif est arrivé.",
    "A fix is planned.": "Un correctif est prévu.",
    "This goes to the makers of Home Checkup. Only what you see here is sent, and only when you press Send.": "Ceci est envoyé aux créateurs de Home Checkup. Seul ce que vous voyez ici est envoyé, et seulement quand vous appuyez sur Envoyer.",
    "Problem": "Problème",
    "Integration": "Intégration",
    "Versions": "Versions",
    "Log error": "Erreur du journal",
    "The error text. Remove anything you do not want to share.": "Le texte de l’erreur. Retirez tout ce que vous ne voulez pas partager.",
    "Add a note (optional)": "Ajouter une note (facultatif)",
    "Your email, only if you want an answer (optional)": "Votre e-mail, seulement si vous voulez une réponse (facultatif)",
    "No device names, no addresses and no account are sent.": "Aucun nom d’appareil, aucune adresse et aucun compte ne sont envoyés.",
    "Send": "Envoyer",
    "Sending…": "Envoi…",
    "Done": "Terminé",
    "Thank you. Your request was received.": "Merci. Votre demande a été reçue.",
    "We read every request and build the most wanted fixes first.": "Nous lisons chaque demande et créons d’abord les correctifs les plus demandés.",
    "A fix for this is already planned.": "Un correctif est déjà prévu.",
    "Good news: this is fixed in version {version}.": "Bonne nouvelle : c’est corrigé dans la version {version}.",
    "Too many requests. Please try again in an hour.": "Trop de demandes. Réessayez dans une heure.",
    "The email address does not look right.": "L’adresse e-mail ne semble pas correcte.",
    "Could not send. Please try again later.": "Envoi impossible. Réessayez plus tard.",
    "{n} to watch": "{n} à surveiller",
    "To watch": "À surveiller",
    "Seen only briefly. These count when they keep coming back.": "Vus brièvement. Ils comptent s’ils reviennent souvent.",
    "{n} of these is written in a YAML file. The button cannot remove it.": "{n} de ces éléments est écrit dans un fichier YAML. Le bouton ne peut pas le supprimer.",
    "{n} of these are written in YAML files. The button cannot remove them.": "{n} de ces éléments sont écrits dans des fichiers YAML. Le bouton ne peut pas les supprimer.",
    "Remove this step": "Retirer cette étape",
    "Removed a step from {name}": "Étape retirée de {name}",
    "Step removed. A backup was made.": "Étape retirée. Une sauvegarde a été faite.",
    "Turn off": "Désactiver",
    "Never ran": "Jamais exécutée",
    "Last ran today": "Exécutée aujourd’hui",
    "Last ran {date}": "Exécutée le {date}",
    "Updated {name}": "{name} mise à jour",
    "Turned off {name}": "{name} désactivée",
    "This automation lives in a YAML file. Open it to change it.": "Cette automatisation est dans un fichier YAML. Ouvrez-la pour la modifier.",
    "It did not fully change. You can undo it.": "Le changement n’est pas complet. Vous pouvez l’annuler.",
    "Updated. A backup was made.": "Mise à jour. Une sauvegarde a été faite.",
    "Turned off. You can turn it on again.": "Désactivée. Vous pouvez la réactiver.",
    "Checked. {n} thing fewer than before.": "Vérifié. {n} point de moins qu’avant.",
    "Checked. {n} things fewer than before.": "Vérifié. {n} points de moins qu’avant.",
    "Checked. {n} new thing to look at.": "Vérifié. {n} nouveau point à vérifier.",
    "Checked. {n} new things to look at.": "Vérifié. {n} nouveaux points à vérifier.",
    "Checked. Nothing changed.": "Vérifié. Rien n’a changé.",
    "An update is ready ({version}). Updates often fix errors like these.": "Une mise à jour est prête ({version}). Elle corrige souvent ce genre d’erreur.",
    "Devices": "Appareils",
    "Device": "Appareil",
    "Dashboards": "Tableaux de bord",
    "Entities": "Entités",
    "Scripts": "Scripts",
    "Update": "Mise à jour",
    "Sign in": "Se connecter",
    "The errors stopped": "Les erreurs ont cessé",
    "No errors since the update.": "Plus d’erreur depuis la mise à jour.",
    "No errors since you signed in again.": "Plus d’erreur depuis votre reconnexion.",
    "No errors since you checked the devices.": "Plus d’erreur depuis que vous avez vérifié les appareils.",
    "No errors since you fixed the template.": "Plus d’erreur depuis que vous avez corrigé le modèle.",
    "No errors since you took the next step.": "Plus d’erreur depuis votre action.",
    "Only right after a restart. Usually harmless, but it hides real errors.": "Seulement juste après un redémarrage. En général sans gravité, mais cela cache les vraies erreurs.",
  },
  de: {
    "Home Checkup": "Zuhause-Check",
    "Home is healthy": "Dem Zuhause geht es gut",
    "{n} thing needs a look": "{n} Punkt zum Ansehen",
    "{n} things need a look": "{n} Punkte zum Ansehen",
    "Nothing changes until you choose to.": "Nichts ändert sich ohne Ihre Wahl.",
    "Nothing needs a look today.": "Heute gibt es nichts zu prüfen.",
    "Checked {time}": "Geprüft um {time}",
    "Not checked yet": "Noch nicht geprüft",
    "Check now": "Jetzt prüfen",
    "Checking…": "Wird geprüft…",
    "Good to know": "Gut zu wissen",
    "Integrations": "Integrationen",
    "Log": "Protokoll",
    "Automations": "Automatisierungen",
    "Leftovers": "Reste",
    "Offline": "Offline",
    "Helpers": "Helfer",
    "{n} integration did not start": "{n} Integration ist nicht gestartet",
    "{n} integrations did not start": "{n} Integrationen sind nicht gestartet",
    "Errors from {name}": "Fehler von {name}",
    "Warnings from {name}": "Warnungen von {name}",
    "{n} broken automation step": "{n} defekter Automationsschritt",
    "{n} broken automation steps": "{n} defekte Automationsschritte",
    "{n} leftover entity": "{n} verwaiste Entität",
    "{n} leftover entities": "{n} verwaiste Entitäten",
    "{n} leftover device": "{n} verwaistes Gerät",
    "{n} leftover devices": "{n} verwaiste Geräte",
    "{n} entity offline for a long time": "{n} Entität lange offline",
    "{n} entities offline for a long time": "{n} Entitäten lange offline",
    "{n} helper nothing seems to use": "{n} Helfer, den nichts zu nutzen scheint",
    "{n} helpers nothing seems to use": "{n} Helfer, die nichts zu nutzen scheint",
    "Their devices do not work until they start again.": "Ihre Geräte funktionieren erst wieder, wenn sie starten.",
    "Grouped by cause, last 24 hours.": "Nach Ursache gruppiert, letzte 24 Stunden.",
    "Usually harmless. Shown, not counted.": "Meist harmlos. Angezeigt, nicht gezählt.",
    "These steps will fail when they run.": "Diese Schritte schlagen beim Ausführen fehl.",
    "Nothing provides them any more.": "Nichts stellt sie mehr bereit.",
    "Their integration is gone.": "Ihre Integration wurde entfernt.",
    "Off, unplugged or out of range.": "Aus, ausgesteckt oder außer Reichweite.",
    "Shown, not counted. Something outside may still use them.": "Angezeigt, nicht gezählt. Etwas außerhalb nutzt sie vielleicht noch.",
    "a removed device": "ein entferntes Gerät",
    "Open": "Öffnen",
    "Ignore": "Ignorieren",
    "Ignore means this is fine. It will not show again.": "Ignorieren heißt: Das ist in Ordnung. Es wird nicht mehr angezeigt.",
    "Show all {n}": "Alle {n} zeigen",
    "Show fewer": "Weniger zeigen",
    "Show the full error": "Vollständigen Fehler zeigen",
    "Show all lines": "Alle Zeilen zeigen",
    "Copy": "Kopieren",
    "Copied": "Kopiert",
    "First seen {when}": "Zuerst gesehen: {when}",
    "{n} integrations checked. All started.": "{n} Integrationen geprüft. Alle sind gestartet.",
    "The log of the last 24 hours was read. No error keeps coming back.": "Das Protokoll der letzten 24 Stunden wurde gelesen. Kein Fehler kommt immer wieder.",
    "{n} automations and scripts checked. No broken steps.": "{n} Automationen und Skripte geprüft. Keine defekten Schritte.",
    "{n} entities and {m} devices checked. No leftovers.": "{n} Entitäten und {m} Geräte geprüft. Keine Überreste.",
    "{n} entities checked. None was offline for a long time.": "{n} Entitäten geprüft. Keine war lange offline.",
    "{n} helpers checked. All are in use.": "{n} Helfer geprüft. Alle werden genutzt.",
    "{n} batteries checked. None is low.": "{n} Batterien geprüft. Keine ist schwach.",
    "Helpers are checked with the next full check.": "Helfer werden bei der nächsten vollen Prüfung geprüft.",
    "Likely from {name}": "Wahrscheinlich von {name}",
    "Last seen {when}": "Zuletzt gesehen: {when}",
    "{n} times in 24 hours": "{n}-mal in 24 Stunden",
    "Known issues": "Bekannte Probleme",
    "Debug logging": "Debug-Protokoll",
    "The integration page has the debug logging switch.": "Die Seite der Integration hat den Schalter für das Debug-Protokoll.",
    "Copies a report you can paste into a bug report.": "Kopiert einen Bericht zum Einfügen in eine Fehlermeldung.",
    "Could not read the full error.": "Der vollständige Fehler konnte nicht gelesen werden.",
    "Ignored. It will not show again.": "Ignoriert. Es wird nicht mehr angezeigt.",
    "Undo": "Rückgängig",
    "Ignored items ({n})": "Ignorierte Einträge ({n})",
    "Show again": "Wieder zeigen",
    "Home Checkup only reads. It never changes, removes or restarts anything by itself.": "Der Zuhause-Check liest nur. Er ändert, entfernt oder startet nichts von selbst neu.",
    "Home Checkup is not set up.": "Der Zuhause-Check ist nicht eingerichtet.",
    "Add it in Settings, Devices and services.": "Fügen Sie ihn unter Einstellungen, Geräte und Dienste hinzu.",
    "Could not load the report.": "Der Bericht konnte nicht geladen werden.",
    "Remove…": "Entfernen…",
    "Remove leftover entities": "Verwaiste Entitäten entfernen",
    "Remove helpers nothing uses": "Ungenutzte Helfer entfernen",
    "Nothing provides these any more. Untick any you want to keep.": "Nichts stellt sie mehr bereit. Entfernen Sie den Haken bei denen, die Sie behalten möchten.",
    "Pick only the ones you are sure about. Something outside Home Assistant, like Node-RED, may still use them.": "Wählen Sie nur die, bei denen Sie sicher sind. Etwas außerhalb von Home Assistant, wie Node-RED, nutzt sie vielleicht noch.",
    "A backup is made first. You can undo this for 30 days.": "Zuerst wird eine Sicherung erstellt. Sie können es 30 Tage lang rückgängig machen.",
    "Tick all": "Alle auswählen",
    "Untick all": "Keine auswählen",
    "Made in YAML. Remove it from your YAML files.": "In YAML erstellt. Entfernen Sie ihn aus Ihren YAML-Dateien.",
    "Nothing to remove.": "Nichts zu entfernen.",
    "Cancel": "Abbrechen",
    "Removing…": "Wird entfernt…",
    "Remove {n}": "{n} entfernen",
    "Remove": "Entfernen",
    "Removed {n}. A backup was made.": "{n} entfernt. Eine Sicherung wurde erstellt.",
    "Removed {n} of {m}. Some did not change. You can undo it.": "{n} von {m} entfernt. Manche haben sich nicht geändert. Sie können es rückgängig machen.",
    "Undone. {n} brought back.": "Rückgängig gemacht. {n} wiederhergestellt.",
    "Something went wrong. Nothing was changed.": "Etwas ist schiefgelaufen. Nichts wurde geändert.",
    "Something went wrong.": "Etwas ist schiefgelaufen.",
    "Recent fixes": "Letzte Korrekturen",
    "Removed {n} leftover entity": "{n} verwaiste Entität entfernt",
    "Removed {n} leftover entities": "{n} verwaiste Entitäten entfernt",
    "Removed {n} helper": "{n} Helfer entfernt",
    "Removed {n} helpers": "{n} Helfer entfernt",
    "Undone": "Rückgängig gemacht",
    "Some did not change": "Manche haben sich nicht geändert",
    "Home Checkup never changes anything by itself. A fix happens only when you tap it.": "Der Zuhause-Check ändert nichts von selbst. Eine Korrektur geschieht nur, wenn Sie sie antippen.",
    "Something points to an entity that no longer exists.": "Etwas verweist auf eine Entität, die es nicht mehr gibt.",
    "It starts slowly. Usually harmless.": "Es startet langsam. Meist harmlos.",
    "Try: {text}": "Versuch: {text}",
    "A dashboard card had a fault in the browser.": "Eine Dashboard-Karte hatte einen Fehler im Browser.",
    "Update that card, then reload the page.": "Aktualisieren Sie diese Karte und laden Sie die Seite neu.",
    "It did not answer in time.": "Es hat nicht rechtzeitig geantwortet.",
    "Check that it is on and close to Wi-Fi.": "Prüfen Sie, ob es an ist und nah am WLAN.",
    "Home Assistant could not reach it.": "Home Assistant konnte es nicht erreichen.",
    "Check that it is on and on the network.": "Prüfen Sie, ob es an ist und im Netzwerk.",
    "Its sign-in no longer works.": "Die Anmeldung funktioniert nicht mehr.",
    "Open the integration and sign in again.": "Öffnen Sie die Integration und melden Sie sich neu an.",
    "The service asked Home Assistant to slow down.": "Der Dienst hat Home Assistant gebeten, langsamer zu werden.",
    "Wait. This usually fixes itself.": "Warten Sie. Das behebt sich meist von selbst.",
    "A secure connection failed.": "Eine sichere Verbindung ist fehlgeschlagen.",
    "Check the address and the certificate.": "Prüfen Sie die Adresse und das Zertifikat.",
    "It was asked to start something that was already running. Usually harmless.": "Es sollte etwas starten, das schon lief. Meist harmlos.",
    "The storage is full.": "Der Speicher ist voll.",
    "Free some space, for example old backups.": "Schaffen Sie Platz, zum Beispiel alte Backups.",
    "Home Assistant ran out of memory.": "Home Assistant hatte keinen freien Arbeitsspeicher mehr.",
    "Restart Home Assistant.": "Starten Sie Home Assistant neu.",
    "Home Assistant is not allowed to open a file.": "Home Assistant darf eine Datei nicht öffnen.",
    "Check the permissions of that file.": "Prüfen Sie die Rechte dieser Datei.",
    "An address could not be found.": "Eine Adresse wurde nicht gefunden.",
    "Check the internet connection.": "Prüfen Sie die Internetverbindung.",
    "The connection dropped. It usually comes back by itself.": "Die Verbindung wurde getrennt. Sie kommt meist von selbst zurück.",
    "The device is offline.": "Das Gerät ist offline.",
    "Check its power and Wi-Fi.": "Prüfen Sie Strom und WLAN.",
    "The service itself had a problem.": "Der Dienst selbst hatte ein Problem.",
    "Something calls an action that does not exist.": "Etwas ruft eine Aktion auf, die es nicht gibt.",
    "Check your automations and cards.": "Prüfen Sie Ihre Automationen und Karten.",
    "It asked for something that does not exist.": "Es hat etwas angefragt, das es nicht gibt.",
    "Update the integration.": "Aktualisieren Sie die Integration.",
    "The integration works in a way Home Assistant warns about.": "Die Integration arbeitet auf eine Art, vor der Home Assistant warnt.",
    "It uses something Home Assistant will remove.": "Es nutzt etwas, das Home Assistant entfernen wird.",
    "A template reads something that is missing.": "Ein Template liest etwas, das fehlt.",
    "Check the template.": "Prüfen Sie das Template.",
    "Something points to an entity that no longer exists.": "Etwas zeigt auf eine Entität, die es nicht mehr gibt.",
    "Change it to an entity that exists.": "Ändern Sie es auf eine Entität, die es gibt.",
    "The device cannot do what was asked.": "Das Gerät kann nicht tun, was verlangt wurde.",
    "Check the automation or card that asked for it.": "Prüfen Sie die Automation oder Karte, die es verlangt hat.",
    "It got an answer it could not read.": "Es bekam eine Antwort, die es nicht lesen konnte.",
    "It got a value it cannot use.": "Es bekam einen Wert, den es nicht nutzen kann.",
    "Check the automation or card that sent it.": "Prüfen Sie die Automation oder Karte, die ihn gesendet hat.",
    "This is a fault in its code.": "Das ist ein Fehler in seinem Code.",
    "Update it. If the error stays, report it to its makers.": "Aktualisieren Sie es. Bleibt der Fehler, melden Sie ihn den Entwicklern.",
    "The history database had a problem. Your history may have a gap.": "Die Verlaufsdatenbank hatte ein Problem. Im Verlauf kann eine Lücke sein.",
    "Batteries": "Batterien",
    "{n} battery running low": "{n} Batterie fast leer",
    "{n} batteries running low": "{n} Batterien fast leer",
    "Change them before the device stops working.": "Tauschen Sie sie, bevor das Gerät ausfällt.",
    "New": "Neu",
    "Renamed to {name}": "Umbenannt in {name}",
    "{name} was removed": "{name} wurde entfernt",
    "Its device was removed": "Sein Gerät wurde entfernt",
    "No longer exists": "Gibt es nicht mehr",
    "Use the new one": "Die neue nutzen",
    "Choose another": "Anderes wählen",
    "Choose what this step should use": "Wählen Sie, was dieser Schritt nutzen soll",
    "{name} points to {old}, which no longer exists. Choose what it should use now. A backup is made first.": "{name} zeigt auf {old}, das es nicht mehr gibt. Wählen Sie, was jetzt genutzt werden soll. Zuerst wird eine Sicherung erstellt.",
    "Search": "Suchen",
    "Nothing of the same kind was found.": "Nichts von derselben Art gefunden.",
    "Written in {file}, line {line}. Change it in that file.": "Steht in {file}, Zeile {line}. Ändern Sie es dort.",
    "This script lives in a YAML file. Open it to change it.": "Dieses Skript liegt in einer YAML-Datei. Öffnen Sie es, um es zu ändern.",
    "Showing the first {n}. Search to find more.": "Die ersten {n} werden gezeigt. Suchen Sie, um mehr zu finden.",
    "Ask": "Anfragen",
    "Ask sends us a request for a fix. You read it first.": "Anfragen sendet uns eine Bitte um eine Lösung. Sie lesen sie zuerst.",
    "Ask for a fix": "Um eine Lösung bitten",
    "Asked": "Angefragt",
    "A fix arrived in version {version}. Update to get it.": "Eine Lösung ist in Version {version} angekommen. Aktualisieren Sie, um sie zu erhalten.",
    "A fix arrived.": "Eine Korrektur ist da.",
    "A fix is planned.": "Eine Lösung ist geplant.",
    "This goes to the makers of Home Checkup. Only what you see here is sent, and only when you press Send.": "Das geht an die Macher von Home Checkup. Nur was Sie hier sehen, wird gesendet, und nur wenn Sie auf Senden drücken.",
    "Problem": "Problem",
    "Integration": "Integration",
    "Versions": "Versionen",
    "Log error": "Protokollfehler",
    "The error text. Remove anything you do not want to share.": "Der Fehlertext. Entfernen Sie alles, was Sie nicht teilen möchten.",
    "Add a note (optional)": "Notiz hinzufügen (optional)",
    "Your email, only if you want an answer (optional)": "Ihre E-Mail, nur wenn Sie eine Antwort möchten (optional)",
    "No device names, no addresses and no account are sent.": "Es werden keine Gerätenamen, keine Adressen und kein Konto gesendet.",
    "Send": "Senden",
    "Sending…": "Wird gesendet…",
    "Done": "Fertig",
    "Thank you. Your request was received.": "Danke. Ihre Anfrage ist angekommen.",
    "We read every request and build the most wanted fixes first.": "Wir lesen jede Anfrage und bauen die meistgewünschten Lösungen zuerst.",
    "A fix for this is already planned.": "Eine Lösung dafür ist bereits geplant.",
    "Good news: this is fixed in version {version}.": "Gute Nachricht: Das ist in Version {version} behoben.",
    "Too many requests. Please try again in an hour.": "Zu viele Anfragen. Bitte versuchen Sie es in einer Stunde erneut.",
    "The email address does not look right.": "Die E-Mail-Adresse sieht nicht richtig aus.",
    "Could not send. Please try again later.": "Senden nicht möglich. Bitte versuchen Sie es später erneut.",
    "{n} to watch": "{n} zum Beobachten",
    "To watch": "Beobachten",
    "Seen only briefly. These count when they keep coming back.": "Nur kurz gesehen. Sie zählen, wenn sie immer wieder auftreten.",
    "{n} of these is written in a YAML file. The button cannot remove it.": "{n} davon steht in einer YAML-Datei. Die Schaltfläche kann ihn nicht entfernen.",
    "{n} of these are written in YAML files. The button cannot remove them.": "{n} davon stehen in YAML-Dateien. Die Schaltfläche kann sie nicht entfernen.",
    "Remove this step": "Diesen Schritt entfernen",
    "Removed a step from {name}": "Schritt aus {name} entfernt",
    "Step removed. A backup was made.": "Schritt entfernt. Eine Sicherung wurde erstellt.",
    "Turn off": "Ausschalten",
    "Never ran": "Nie gelaufen",
    "Last ran today": "Heute gelaufen",
    "Last ran {date}": "Zuletzt am {date}",
    "Updated {name}": "{name} aktualisiert",
    "Turned off {name}": "{name} ausgeschaltet",
    "This automation lives in a YAML file. Open it to change it.": "Diese Automation steht in einer YAML-Datei. Öffne sie, um sie zu ändern.",
    "It did not fully change. You can undo it.": "Es hat sich nicht ganz geändert. Du kannst es rückgängig machen.",
    "Updated. A backup was made.": "Aktualisiert. Eine Sicherung wurde erstellt.",
    "Turned off. You can turn it on again.": "Ausgeschaltet. Du kannst sie wieder einschalten.",
    "Checked. {n} thing fewer than before.": "Geprüft. {n} Punkt weniger als vorher.",
    "Checked. {n} things fewer than before.": "Geprüft. {n} Punkte weniger als vorher.",
    "Checked. {n} new thing to look at.": "Geprüft. {n} neuer Punkt zum Ansehen.",
    "Checked. {n} new things to look at.": "Geprüft. {n} neue Punkte zum Ansehen.",
    "Checked. Nothing changed.": "Geprüft. Nichts hat sich geändert.",
    "An update is ready ({version}). Updates often fix errors like these.": "Ein Update ist bereit ({version}). Updates beheben solche Fehler oft.",
    "Devices": "Geräte",
    "Device": "Gerät",
    "Dashboards": "Dashboards",
    "Entities": "Entitäten",
    "Scripts": "Skripte",
    "Update": "Update",
    "Sign in": "Anmelden",
    "The errors stopped": "Die Fehler haben aufgehört",
    "No errors since the update.": "Keine Fehler seit dem Update.",
    "No errors since you signed in again.": "Keine Fehler, seit du dich neu angemeldet hast.",
    "No errors since you checked the devices.": "Keine Fehler, seit du die Geräte geprüft hast.",
    "No errors since you fixed the template.": "Keine Fehler, seit du die Vorlage korrigiert hast.",
    "No errors since you took the next step.": "Keine Fehler seit deinem nächsten Schritt.",
    "Only right after a restart. Usually harmless, but it hides real errors.": "Nur direkt nach einem Neustart. Meist harmlos, aber es verdeckt echte Fehler.",
  },
  es: {
    "Home Checkup": "Chequeo del hogar",
    "Home is healthy": "La casa está bien",
    "{n} thing needs a look": "{n} cosa para revisar",
    "{n} things need a look": "{n} cosas para revisar",
    "Nothing changes until you choose to.": "Nada cambia hasta que usted lo decida.",
    "Nothing needs a look today.": "Hoy no hay nada que revisar.",
    "Checked {time}": "Revisado a las {time}",
    "Not checked yet": "Aún no revisado",
    "Check now": "Revisar ahora",
    "Checking…": "Revisando…",
    "Good to know": "Bueno saberlo",
    "Integrations": "Integraciones",
    "Log": "Registro",
    "Automations": "Automatizaciones",
    "Leftovers": "Sobrantes",
    "Offline": "Sin conexión",
    "Helpers": "Ayudantes",
    "{n} integration did not start": "{n} integración no arrancó",
    "{n} integrations did not start": "{n} integraciones no arrancaron",
    "Errors from {name}": "Errores de {name}",
    "Warnings from {name}": "Avisos de {name}",
    "{n} broken automation step": "{n} paso de automatización roto",
    "{n} broken automation steps": "{n} pasos de automatización rotos",
    "{n} leftover entity": "{n} entidad sobrante",
    "{n} leftover entities": "{n} entidades sobrantes",
    "{n} leftover device": "{n} dispositivo sobrante",
    "{n} leftover devices": "{n} dispositivos sobrantes",
    "{n} entity offline for a long time": "{n} entidad sin conexión hace tiempo",
    "{n} entities offline for a long time": "{n} entidades sin conexión hace tiempo",
    "{n} helper nothing seems to use": "{n} ayudante que nada parece usar",
    "{n} helpers nothing seems to use": "{n} ayudantes que nada parece usar",
    "Their devices do not work until they start again.": "Sus dispositivos no funcionan hasta que vuelvan a arrancar.",
    "Grouped by cause, last 24 hours.": "Agrupados por causa, últimas 24 horas.",
    "Usually harmless. Shown, not counted.": "Suelen ser inofensivos. Se muestran, no se cuentan.",
    "These steps will fail when they run.": "Estos pasos fallarán al ejecutarse.",
    "Nothing provides them any more.": "Ya nada los proporciona.",
    "Their integration is gone.": "Su integración ya no está.",
    "Off, unplugged or out of range.": "Apagados, desenchufados o fuera de alcance.",
    "Shown, not counted. Something outside may still use them.": "Se muestran, no se cuentan. Algo externo puede usarlos aún.",
    "a removed device": "un dispositivo eliminado",
    "Open": "Abrir",
    "Ignore": "Ignorar",
    "Ignore means this is fine. It will not show again.": "Ignorar significa que está bien. No volverá a mostrarse.",
    "Show all {n}": "Mostrar los {n}",
    "Show fewer": "Mostrar menos",
    "Show the full error": "Mostrar el error completo",
    "Show all lines": "Mostrar todas las líneas",
    "Copy": "Copiar",
    "Copied": "Copiado",
    "First seen {when}": "Visto por primera vez: {when}",
    "{n} integrations checked. All started.": "{n} integraciones comprobadas. Todas se iniciaron.",
    "The log of the last 24 hours was read. No error keeps coming back.": "Se leyó el registro de las últimas 24 horas. Ningún error se repite.",
    "{n} automations and scripts checked. No broken steps.": "{n} automatizaciones y scripts comprobados. Ningún paso roto.",
    "{n} entities and {m} devices checked. No leftovers.": "{n} entidades y {m} dispositivos comprobados. Sin restos.",
    "{n} entities checked. None was offline for a long time.": "{n} entidades comprobadas. Ninguna estuvo mucho tiempo sin conexión.",
    "{n} helpers checked. All are in use.": "{n} ayudantes comprobados. Todos se usan.",
    "{n} batteries checked. None is low.": "{n} baterías comprobadas. Ninguna está baja.",
    "Helpers are checked with the next full check.": "Los ayudantes se comprueban en la próxima comprobación completa.",
    "Likely from {name}": "Probablemente de {name}",
    "Last seen {when}": "Visto por última vez: {when}",
    "{n} times in 24 hours": "{n} veces en 24 horas",
    "Known issues": "Problemas conocidos",
    "Debug logging": "Registro de depuración",
    "The integration page has the debug logging switch.": "La página de la integración tiene el interruptor del registro de depuración.",
    "Copies a report you can paste into a bug report.": "Copia un informe para pegar en un aviso de error.",
    "Could not read the full error.": "No se pudo leer el error completo.",
    "Ignored. It will not show again.": "Ignorado. No volverá a mostrarse.",
    "Undo": "Deshacer",
    "Ignored items ({n})": "Elementos ignorados ({n})",
    "Show again": "Mostrar de nuevo",
    "Home Checkup only reads. It never changes, removes or restarts anything by itself.": "El chequeo solo lee. Nunca cambia, elimina ni reinicia nada por sí mismo.",
    "Home Checkup is not set up.": "El chequeo del hogar no está configurado.",
    "Add it in Settings, Devices and services.": "Añádalo en Ajustes, Dispositivos y servicios.",
    "Could not load the report.": "No se pudo cargar el informe.",
    "Remove…": "Quitar…",
    "Remove leftover entities": "Quitar entidades sobrantes",
    "Remove helpers nothing uses": "Quitar ayudantes sin uso",
    "Nothing provides these any more. Untick any you want to keep.": "Ya nada las proporciona. Desmarque las que quiera conservar.",
    "Pick only the ones you are sure about. Something outside Home Assistant, like Node-RED, may still use them.": "Elija solo los que tenga claros. Algo fuera de Home Assistant, como Node-RED, puede usarlos aún.",
    "A backup is made first. You can undo this for 30 days.": "Primero se hace una copia de seguridad. Puede deshacerlo durante 30 días.",
    "Tick all": "Marcar todo",
    "Untick all": "Desmarcar todo",
    "Made in YAML. Remove it from your YAML files.": "Creado en YAML. Quítelo de sus archivos YAML.",
    "Nothing to remove.": "Nada que quitar.",
    "Cancel": "Cancelar",
    "Removing…": "Quitando…",
    "Remove {n}": "Quitar {n}",
    "Remove": "Quitar",
    "Removed {n}. A backup was made.": "{n} quitado(s). Se hizo una copia de seguridad.",
    "Removed {n} of {m}. Some did not change. You can undo it.": "{n} de {m} quitados. Algunos no cambiaron. Puede deshacerlo.",
    "Undone. {n} brought back.": "Deshecho. {n} recuperado(s).",
    "Something went wrong. Nothing was changed.": "Algo salió mal. No se cambió nada.",
    "Something went wrong.": "Algo salió mal.",
    "Recent fixes": "Arreglos recientes",
    "Removed {n} leftover entity": "{n} entidad sobrante quitada",
    "Removed {n} leftover entities": "{n} entidades sobrantes quitadas",
    "Removed {n} helper": "{n} ayudante quitado",
    "Removed {n} helpers": "{n} ayudantes quitados",
    "Undone": "Deshecho",
    "Some did not change": "Algunos no cambiaron",
    "Home Checkup never changes anything by itself. A fix happens only when you tap it.": "El chequeo no cambia nada por sí mismo. Un arreglo solo ocurre cuando usted lo toca.",
    "Something points to an entity that no longer exists.": "Algo apunta a una entidad que ya no existe.",
    "It starts slowly. Usually harmless.": "Arranca despacio. Suele ser inofensivo.",
    "Try: {text}": "Pruebe: {text}",
    "A dashboard card had a fault in the browser.": "Una tarjeta del panel tuvo un fallo en el navegador.",
    "Update that card, then reload the page.": "Actualice esa tarjeta y recargue la página.",
    "It did not answer in time.": "No respondió a tiempo.",
    "Check that it is on and close to Wi-Fi.": "Compruebe que está encendido y cerca del Wi-Fi.",
    "Home Assistant could not reach it.": "Home Assistant no pudo conectar con él.",
    "Check that it is on and on the network.": "Compruebe que está encendido y en la red.",
    "Its sign-in no longer works.": "Su inicio de sesión ya no funciona.",
    "Open the integration and sign in again.": "Abra la integración e inicie sesión de nuevo.",
    "The service asked Home Assistant to slow down.": "El servicio pidió a Home Assistant que vaya más despacio.",
    "Wait. This usually fixes itself.": "Espere. Suele arreglarse solo.",
    "A secure connection failed.": "Falló una conexión segura.",
    "Check the address and the certificate.": "Compruebe la dirección y el certificado.",
    "It was asked to start something that was already running. Usually harmless.": "Se le pidió iniciar algo que ya estaba en marcha. Suele ser inofensivo.",
    "The storage is full.": "El almacenamiento está lleno.",
    "Free some space, for example old backups.": "Libere espacio, por ejemplo copias de seguridad antiguas.",
    "Home Assistant ran out of memory.": "Home Assistant se quedó sin memoria.",
    "Restart Home Assistant.": "Reinicie Home Assistant.",
    "Home Assistant is not allowed to open a file.": "Home Assistant no tiene permiso para abrir un archivo.",
    "Check the permissions of that file.": "Compruebe los permisos de ese archivo.",
    "An address could not be found.": "No se encontró una dirección.",
    "Check the internet connection.": "Compruebe la conexión a Internet.",
    "The connection dropped. It usually comes back by itself.": "La conexión se cortó. Suele volver sola.",
    "The device is offline.": "El dispositivo está sin conexión.",
    "Check its power and Wi-Fi.": "Compruebe su alimentación y el Wi-Fi.",
    "The service itself had a problem.": "El propio servicio tuvo un problema.",
    "Something calls an action that does not exist.": "Algo llama a una acción que no existe.",
    "Check your automations and cards.": "Compruebe sus automatizaciones y tarjetas.",
    "It asked for something that does not exist.": "Pidió algo que no existe.",
    "Update the integration.": "Actualice la integración.",
    "The integration works in a way Home Assistant warns about.": "La integración trabaja de una forma sobre la que Home Assistant avisa.",
    "It uses something Home Assistant will remove.": "Usa algo que Home Assistant va a retirar.",
    "A template reads something that is missing.": "Una plantilla lee algo que falta.",
    "Check the template.": "Compruebe la plantilla.",
    "Something points to an entity that no longer exists.": "Algo apunta a una entidad que ya no existe.",
    "Change it to an entity that exists.": "Cámbielo por una entidad que exista.",
    "The device cannot do what was asked.": "El dispositivo no puede hacer lo que se pidió.",
    "Check the automation or card that asked for it.": "Compruebe la automatización o la tarjeta que lo pidió.",
    "It got an answer it could not read.": "Recibió una respuesta que no pudo leer.",
    "It got a value it cannot use.": "Recibió un valor que no puede usar.",
    "Check the automation or card that sent it.": "Compruebe la automatización o la tarjeta que lo envió.",
    "This is a fault in its code.": "Es un fallo en su código.",
    "Update it. If the error stays, report it to its makers.": "Actualícelo. Si el error sigue, avise a sus autores.",
    "The history database had a problem. Your history may have a gap.": "La base de datos del historial tuvo un problema. Puede haber un hueco en el historial.",
    "Batteries": "Pilas",
    "{n} battery running low": "{n} pila casi agotada",
    "{n} batteries running low": "{n} pilas casi agotadas",
    "Change them before the device stops working.": "Cámbielas antes de que el dispositivo deje de funcionar.",
    "New": "Nuevo",
    "Renamed to {name}": "Renombrado a {name}",
    "{name} was removed": "Se quitó {name}",
    "Its device was removed": "Se quitó su dispositivo",
    "No longer exists": "Ya no existe",
    "Use the new one": "Usar el nuevo",
    "Choose another": "Elegir otro",
    "Choose what this step should use": "Elija lo que este paso debe usar",
    "{name} points to {old}, which no longer exists. Choose what it should use now. A backup is made first.": "{name} apunta a {old}, que ya no existe. Elija lo que debe usar ahora. Primero se hace una copia de seguridad.",
    "Search": "Buscar",
    "Nothing of the same kind was found.": "No se encontró nada del mismo tipo.",
    "Written in {file}, line {line}. Change it in that file.": "Escrito en {file}, línea {line}. Cámbielo en ese archivo.",
    "This script lives in a YAML file. Open it to change it.": "Este script está en un archivo YAML. Ábralo para cambiarlo.",
    "Showing the first {n}. Search to find more.": "Se muestran los primeros {n}. Busque para encontrar más.",
    "Ask": "Pedir",
    "Ask sends us a request for a fix. You read it first.": "Pedir nos envía una solicitud de solución. Usted la lee primero.",
    "Ask for a fix": "Pedir una solución",
    "Asked": "Pedido",
    "A fix arrived in version {version}. Update to get it.": "Llegó una solución en la versión {version}. Actualice para obtenerla.",
    "A fix arrived.": "Llegó una corrección.",
    "A fix is planned.": "Hay una solución prevista.",
    "This goes to the makers of Home Checkup. Only what you see here is sent, and only when you press Send.": "Esto se envía a los creadores de Home Checkup. Solo se envía lo que ve aquí, y solo cuando pulsa Enviar.",
    "Problem": "Problema",
    "Integration": "Integración",
    "Versions": "Versiones",
    "Log error": "Error del registro",
    "The error text. Remove anything you do not want to share.": "El texto del error. Quite todo lo que no quiera compartir.",
    "Add a note (optional)": "Añadir una nota (opcional)",
    "Your email, only if you want an answer (optional)": "Su correo, solo si quiere una respuesta (opcional)",
    "No device names, no addresses and no account are sent.": "No se envían nombres de dispositivos, direcciones ni cuentas.",
    "Send": "Enviar",
    "Sending…": "Enviando…",
    "Done": "Listo",
    "Thank you. Your request was received.": "Gracias. Hemos recibido su solicitud.",
    "We read every request and build the most wanted fixes first.": "Leemos cada solicitud y creamos primero las soluciones más pedidas.",
    "A fix for this is already planned.": "Ya hay una solución prevista.",
    "Good news: this is fixed in version {version}.": "Buenas noticias: está resuelto en la versión {version}.",
    "Too many requests. Please try again in an hour.": "Demasiadas solicitudes. Inténtelo de nuevo en una hora.",
    "The email address does not look right.": "La dirección de correo no parece correcta.",
    "Could not send. Please try again later.": "No se pudo enviar. Inténtelo más tarde.",
    "{n} to watch": "{n} para vigilar",
    "To watch": "Para vigilar",
    "Seen only briefly. These count when they keep coming back.": "Vistos solo un momento. Cuentan si siguen volviendo.",
    "{n} of these is written in a YAML file. The button cannot remove it.": "{n} de estos está escrito en un archivo YAML. El botón no puede quitarlo.",
    "{n} of these are written in YAML files. The button cannot remove them.": "{n} de estos están escritos en archivos YAML. El botón no puede quitarlos.",
    "Remove this step": "Quitar este paso",
    "Removed a step from {name}": "Paso quitado de {name}",
    "Step removed. A backup was made.": "Paso quitado. Se hizo una copia de seguridad.",
    "Turn off": "Desactivar",
    "Never ran": "Nunca se ejecutó",
    "Last ran today": "Se ejecutó hoy",
    "Last ran {date}": "Última vez el {date}",
    "Updated {name}": "{name} actualizada",
    "Turned off {name}": "{name} desactivada",
    "This automation lives in a YAML file. Open it to change it.": "Esta automatización está en un archivo YAML. Ábrala para cambiarla.",
    "It did not fully change. You can undo it.": "No cambió del todo. Puede deshacerlo.",
    "Updated. A backup was made.": "Actualizada. Se hizo una copia de seguridad.",
    "Turned off. You can turn it on again.": "Desactivada. Puede volver a activarla.",
    "Checked. {n} thing fewer than before.": "Revisado. {n} punto menos que antes.",
    "Checked. {n} things fewer than before.": "Revisado. {n} puntos menos que antes.",
    "Checked. {n} new thing to look at.": "Revisado. {n} punto nuevo para revisar.",
    "Checked. {n} new things to look at.": "Revisado. {n} puntos nuevos para revisar.",
    "Checked. Nothing changed.": "Revisado. Nada cambió.",
    "An update is ready ({version}). Updates often fix errors like these.": "Hay una actualización lista ({version}). Suele corregir errores como estos.",
    "Devices": "Dispositivos",
    "Device": "Dispositivo",
    "Dashboards": "Paneles",
    "Entities": "Entidades",
    "Scripts": "Scripts",
    "Update": "Actualización",
    "Sign in": "Iniciar sesión",
    "The errors stopped": "Los errores pararon",
    "No errors since the update.": "Sin errores desde la actualización.",
    "No errors since you signed in again.": "Sin errores desde que volvió a iniciar sesión.",
    "No errors since you checked the devices.": "Sin errores desde que revisó los dispositivos.",
    "No errors since you fixed the template.": "Sin errores desde que corrigió la plantilla.",
    "No errors since you took the next step.": "Sin errores desde su último paso.",
    "Only right after a restart. Usually harmless, but it hides real errors.": "Solo justo después de reiniciar. Suele ser inofensivo, pero oculta errores reales.",
  },
};

const CHECKS = [
  ["Integrations", ["failed_integrations"]],
  ["Log", ["log_errors", "log_warnings", "log_stopped"]],
  ["Automations", ["broken_references"]],
  ["Leftovers", ["leftover_entities", "leftover_devices"]],
  ["Offline", ["unavailable"]],
  ["Helpers", ["unused_helpers"]],
  ["Batteries", ["low_batteries"]],
];

/** What a log error means, by the code Home Checkup gives it. */
const MEANINGS = {
  card: "A dashboard card had a fault in the browser.",
  timeout: "It did not answer in time.",
  unreachable: "Home Assistant could not reach it.",
  signin: "Its sign-in no longer works.",
  slowdown: "The service asked Home Assistant to slow down.",
  certificate: "A secure connection failed.",
  already: "It was asked to start something that was already running. Usually harmless.",
  storage: "The storage is full.",
  memory: "Home Assistant ran out of memory.",
  permission: "Home Assistant is not allowed to open a file.",
  dns: "An address could not be found.",
  dropped: "The connection dropped. It usually comes back by itself.",
  offline: "The device is offline.",
  server: "The service itself had a problem.",
  noaction: "Something calls an action that does not exist.",
  notfound: "It asked for something that does not exist.",
  blocking: "The integration works in a way Home Assistant warns about.",
  deprecated: "It uses something Home Assistant will remove.",
  template: "A template reads something that is missing.",
  missing: "Something points to an entity that no longer exists.",
  slowstart: "It starts slowly. Usually harmless.",
  unsupported: "The device cannot do what was asked.",
  baddata: "It got an answer it could not read.",
  badvalue: "It got a value it cannot use.",
  database: "The history database had a problem. Your history may have a gap.",
  bug: "This is a fault in its code.",
};

/** One safe thing to try, for the meanings that have one. */
const TRY = {
  card: "Update that card, then reload the page.",
  timeout: "Check that it is on and close to Wi-Fi.",
  unreachable: "Check that it is on and on the network.",
  signin: "Open the integration and sign in again.",
  slowdown: "Wait. This usually fixes itself.",
  certificate: "Check the address and the certificate.",
  storage: "Free some space, for example old backups.",
  memory: "Restart Home Assistant.",
  permission: "Check the permissions of that file.",
  dns: "Check the internet connection.",
  offline: "Check its power and Wi-Fi.",
  server: "Wait. This usually fixes itself.",
  noaction: "Check your automations and cards.",
  notfound: "Update the integration.",
  blocking: "Update the integration.",
  deprecated: "Update the integration.",
  template: "Check the template.",
  missing: "Change it to an entity that exists.",
  unsupported: "Check the automation or card that asked for it.",
  baddata: "Update the integration.",
  badvalue: "Check the automation or card that sent it.",
  bug: "Update it. If the error stays, report it to its makers.",
};

/** What a green chip says when tapped: the words, then the counts it uses ({n}, then {m}). */
const CHECKED = {
  Integrations: ["{n} integrations checked. All started.", "integrations"],
  Log: ["The log of the last 24 hours was read. No error keeps coming back."],
  Automations: ["{n} automations and scripts checked. No broken steps.", "automations"],
  Leftovers: ["{n} entities and {m} devices checked. No leftovers.", "entities", "devices"],
  Offline: ["{n} entities checked. None was offline for a long time.", "states"],
  Helpers: ["{n} helpers checked. All are in use.", "helpers"],
  Batteries: ["{n} batteries checked. None is low.", "batteries"],
};

const TITLES = {
  failed_integrations: ["{n} integration did not start", "{n} integrations did not start"],
  broken_references: ["{n} broken automation step", "{n} broken automation steps"],
  leftover_entities: ["{n} leftover entity", "{n} leftover entities"],
  leftover_devices: ["{n} leftover device", "{n} leftover devices"],
  unavailable: ["{n} entity offline for a long time", "{n} entities offline for a long time"],
  unused_helpers: ["{n} helper nothing seems to use", "{n} helpers nothing seems to use"],
  low_batteries: ["{n} battery running low", "{n} batteries running low"],
};

const HINTS = {
  failed_integrations: "Their devices do not work until they start again.",
  log_errors: "Grouped by cause, last 24 hours.",
  log_warnings: "Usually harmless. Shown, not counted.",
  broken_references: "These steps will fail when they run.",
  leftover_entities: "Nothing provides them any more.",
  leftover_devices: "Their integration is gone.",
  unavailable: "Off, unplugged or out of range.",
  unused_helpers: "Shown, not counted. Something outside may still use them.",
  low_batteries: "Change them before the device stops working.",
};

/** The one next step for a group of log errors: [the line, the button]. */
const STEPS = {
  update: ["An update is ready ({version}). Updates often fix errors like these.", "Update"],
  signin: ["", "Sign in"],
  devices: ["", "Devices"],
  template: ["", "Dashboards"],
  logs: ["", "Log"],
};

/** The short name of the Home Assistant page a link goes to. One word, so the card stays calm. */
const PLACES = [
  ["/config/logs", "Log"],
  ["/config/integrations/integration/", "Integration"],
  ["/config/integrations", "Integrations"],
  ["/config/devices/device/", "Device"],
  ["/config/devices", "Devices"],
  ["/config/entities", "Entities"],
  ["/config/automation", "Automations"],
  ["/config/script", "Scripts"],
  ["/config/helpers", "Helpers"],
  ["/config/lovelace", "Dashboards"],
];
const placeName = (link) => (PLACES.find(([start]) => (link || "").startsWith(start)) || ["", "Open"])[1];
/** A small arrow after each link: it goes to another page of Home Assistant. */
const ARROW =
  '<svg class="arrow" viewBox="0 0 24 24" width="14" height="14" aria-hidden="true"><path d="M8 7h9v9M17 7 7 17" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';

/** "The errors stopped": what the person did. */
const STOPPED = {
  update: "No errors since the update.",
  signin: "No errors since you signed in again.",
  devices: "No errors since you checked the devices.",
  template: "No errors since you fixed the template.",
};

const SHOWN = 8;

/** A copy of an automation with one entity id swapped for another, everywhere it is written (also inside templates). */
const swapEntity = (value, from, to) => {
  if (typeof value === "string") {
    const re = new RegExp(`(?<![\\w.])${from.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}(?![\\w])`, "g");
    return value.replace(re, to);
  }
  if (Array.isArray(value)) return value.map((v) => swapEntity(v, from, to));
  if (value && typeof value === "object") return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, swapEntity(v, from, to)]));
  return value;
};

const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

/** The ring with a heartbeat: green when all is well, amber when something needs a look. */
const mark = (level) => `
  <svg class="mark ${level}" viewBox="0 0 50 50" aria-hidden="true">
    <circle cx="25" cy="25" r="22" />
    <path d="M8 25h9l3-7 5 15 4-12 2 4h9" />
  </svg>`;

/** True when version `a` is newer than version `b` ("0.6.10" is newer than "0.6.9"). An unknown `b` counts as old. */
function newerVersion(a, b) {
  const parts = (v) => String(v).split(/[.\-+]/).map((p) => parseInt(p, 10) || 0);
  const x = parts(a);
  const y = parts(b);
  for (let i = 0; i < Math.max(x.length, y.length); i++) {
    if ((x[i] || 0) !== (y[i] || 0)) return (x[i] || 0) > (y[i] || 0);
  }
  return false;
}

// "Ask for a fix": where a request goes when someone presses Send, and which kinds of line offer it.
const ASK_URL = "https://lukaps.com/homecheckup/api/ask.php";
const STATUS_URL = "https://lukaps.com/homecheckup/api/status.php";
const CHOOSE_SHOWN = 40; // choices shown at once in "Choose another"
const NEWS_EVERY = 6 * 3600 * 1000; // how often the page asks what happened to the requests of this browser
const DETAIL_LINES = 12; // lines of a long error shown before "Show all lines"
const ASK_KINDS = ["log_errors", "broken_references", "failed_integrations"];

class HomeCheckupPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._report = null;
    this._error = "";
    this._open = new Set();
    this._scanning = false;
    this._toast = null;
    this._chip = ""; // the green chip whose "what was checked" line is open
    this._keptOpen = false;
    this._details = {}; // the log lines the person opened: key -> { data, error, all, copied }
    this._sheet = null;
    this._ask = null;
    this._choose = null;
    this._undoing = null;
    this._seen = "";
  }

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    if (this._menu) {
      this._menu.hass = hass;
    }
    const sensor = this._sensor();
    const stamp = sensor ? sensor.last_updated : "";
    if (first || stamp !== this._seen) {
      this._seen = stamp;
      this._load();
    }
  }

  set narrow(narrow) {
    this._narrow = narrow;
    if (this._menu) this._menu.narrow = narrow;
  }

  set panel(_panel) {}

  connectedCallback() {
    if (!this._report && !this._error) this._render();
  }

  // ---- words -------------------------------------------------------------------------------------------------

  _lang() {
    const l = (this._hass?.locale?.language || this._hass?.language || "en").slice(0, 2);
    return WORDS[l] ? l : "en";
  }

  _t(text, vars = {}) {
    const out = WORDS[this._lang()][text] ?? text;
    return out.replace(/\{(\w+)\}/g, (_, k) => (k in vars ? vars[k] : `{${k}}`));
  }

  _tn(n, one, many) {
    return this._t(n === 1 ? one : many, { n });
  }

  _title(f) {
    const n = f.count ?? f.items?.length ?? 0;
    const who = f.integration_name || "Home Assistant";
    if (f.kind === "log_errors") return this._t("Errors from {name}", { name: who });
    if (f.kind === "log_warnings") return this._t("Warnings from {name}", { name: who });
    if (f.kind === "log_stopped") return `${who}: ${this._t("The errors stopped")}`;
    const pair = TITLES[f.kind];
    return pair ? this._tn(n, pair[0], pair[1]) : f.title;
  }

  _headline(n) {
    return n === 0 ? this._t("Home is healthy") : this._tn(n, "{n} thing needs a look", "{n} things need a look");
  }

  _time(iso) {
    try {
      return new Date(iso).toLocaleTimeString(this._hass?.locale?.language || undefined, { hour: "numeric", minute: "2-digit" });
    } catch {
      return "";
    }
  }

  /** What a broken step pointed to, in words: "Porch lantern". */
  _target(it) {
    if (!it.key?.startsWith("ref:")) return "";
    const target = it.key.split(":").slice(2).join(":");
    if (target.startsWith("a removed device")) return this._t("a removed device");
    const state = this._hass?.states?.[target];
    if (state?.attributes?.friendly_name) return state.attributes.friendly_name;
    const object = target.split(".")[1] ?? target;
    return object.replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase());
  }

  /** A kept item in words, from its key ("unavailable:sensor.porch" becomes "Porch"). */
  _keptName(key) {
    const parts = key.split(":");
    const last = parts[parts.length - 1];
    const state = this._hass?.states?.[last];
    if (state?.attributes?.friendly_name) return state.attributes.friendly_name;
    if (parts[0] === "log") return parts.slice(2).join(":");
    return last.includes(".") ? last.split(".")[1].replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase()) : last;
  }

  // ---- data --------------------------------------------------------------------------------------------------

  _sensor() {
    const states = this._hass?.states ?? {};
    if (states["sensor.home_checkup_things_to_look_at"]) return states["sensor.home_checkup_things_to_look_at"];
    for (const id in states) {
      if (!id.startsWith("sensor.home_checkup")) continue;
      const a = states[id].attributes;
      if ("headline" in a && "status" in a && "scanned_at" in a) return states[id];
    }
    return undefined;
  }

  async _call(msg) {
    try {
      this._report = await this._hass.callWS(msg);
      this._error = "";
      this._checkNews();
    } catch (err) {
      this._error = err?.code === "not_loaded" ? "not_loaded" : "failed";
    }
    this._render();
  }

  _load() {
    return this._call({ type: "home_checkup/report" });
  }

  async _scan(say = false) {
    if (this._scanning) return;
    const before = this._report?.count;
    this._scanning = true;
    this._render();
    await this._call({ type: "home_checkup/scan" });
    this._scanning = false;
    if (!say || this._error || before == null) return this._render();
    // Say what the check found, so pressing the button visibly does something.
    const diff = before - (this._report?.count ?? 0);
    const text =
      diff > 0
        ? this._tn(diff, "Checked. {n} thing fewer than before.", "Checked. {n} things fewer than before.")
        : diff < 0
          ? this._tn(-diff, "Checked. {n} new thing to look at.", "Checked. {n} new things to look at.")
          : this._t("Checked. Nothing changed.");
    this._say({ text });
  }

  async _keep(key, keep) {
    await this._call({ type: "home_checkup/keep", key, keep });
    this._say(keep ? { text: this._t("Ignored. It will not show again."), act: "undo", data: key } : null);
  }

  _say(toast) {
    clearTimeout(this._toastTimer);
    this._toast = toast;
    if (toast) this._toastTimer = setTimeout(() => ((this._toast = null), this._render()), 10000);
    this._render();
  }

  // ---- safe fixes ------------------------------------------------------------------------------------------
  // The exact list first (from Home Checkup), a backup, then the change, then a count. Undo for 30 days.

  async _openFix(kind) {
    this._sheet = { kind, busy: true, items: [], error: "" };
    this._render();
    try {
      const plan = await this._hass.callWS({ type: "home_checkup/fix_plan", kind });
      let items = plan.items.map((it) => ({ ...it, on: kind === "leftover_entities", ok: true }));
      if (kind === "unused_helpers") {
        // Only helpers made in the UI can be removed here; Home Assistant's own helper list says which ones.
        const lists = {};
        for (const domain of new Set(items.map((it) => it.domain))) {
          try {
            lists[domain] = await this._hass.callWS({ type: `${domain}/list` });
          } catch {
            lists[domain] = [];
          }
        }
        items = items.map((it) => {
          const item = (lists[it.domain] || []).find((x) => x.id === it.item_id);
          return { ...it, item, ok: !!item, on: false };
        });
      }
      this._sheet = { kind, plan_id: plan.plan_id, items, busy: false, error: "" };
    } catch (err) {
      this._sheet = { kind, items: [], busy: false, error: err?.message || this._t("Something went wrong. Nothing was changed.") };
    }
    this._render();
  }

  async _runFix() {
    const sheet = this._sheet;
    const chosen = sheet.items.filter((it) => it.on && it.ok);
    if (!chosen.length || sheet.busy) return;
    sheet.busy = true;
    sheet.error = "";
    this._render();
    try {
      let result;
      const keys = chosen.map((it) => it.key);
      if (sheet.kind === "leftover_entities") {
        result = await this._hass.callWS({ type: "home_checkup/fix_entities", plan_id: sheet.plan_id, keys });
      } else {
        const saved = chosen.map((it) => ({ entity_id: it.id, domain: it.domain, item: it.item }));
        const start = await this._hass.callWS({ type: "home_checkup/fix_helpers_start", plan_id: sheet.plan_id, keys, saved });
        for (const it of chosen) {
          try {
            await this._hass.callWS({ type: `${it.domain}/delete`, [`${it.domain}_id`]: it.item_id });
          } catch {
            // counted below: the check after says how many really went
          }
        }
        result = await this._hass.callWS({ type: "home_checkup/fix_helpers_finish", fix_id: start.fix.id });
      }
      this._report = result.report;
      this._sheet = null;
      const fix = result.fix;
      const text =
        fix.status === "done"
          ? this._t("Removed {n}. A backup was made.", { n: fix.removed })
          : this._t("Removed {n} of {m}. Some did not change. You can undo it.", { n: fix.removed, m: fix.asked });
      this._say({ text, act: "fixundo", data: fix.id });
      this._scan(); // a fresh list right after a fix
    } catch (err) {
      sheet.busy = false;
      sheet.error = err?.message || this._t("Something went wrong. Nothing was changed.");
      this._render();
    }
  }

  _lastRan(iso) {
    if (!iso) return this._t("Never ran");
    const d = new Date(iso);
    if (isNaN(d)) return "";
    const today = new Date();
    if (d.toDateString() === today.toDateString()) return this._t("Last ran today");
    const sameYear = d.getFullYear() === today.getFullYear();
    const date = d.toLocaleDateString(this._hass?.locale?.language || undefined, sameYear ? { day: "numeric", month: "short" } : { month: "short", year: "numeric" });
    return this._t("Last ran {date}", { date });
  }

  _barIsAccent() {
    try {
      const style = getComputedStyle(this);
      const probe = (value) => {
        const el = document.createElement("span");
        el.style.color = value;
        this.shadowRoot.append(el);
        const out = getComputedStyle(el).color;
        el.remove();
        return out;
      };
      const bar = style.getPropertyValue("--app-header-background-color").trim();
      const accent = style.getPropertyValue("--primary-color").trim();
      return Boolean(bar && accent) && probe(bar) === probe(accent);
    } catch {
      return false;
    }
  }

  // ---- broken automation steps: one tap, with a backup and Undo. Home Assistant's own automation editor does the change.

  _autoId(item) {
    const m = /\/config\/automation\/edit\/([^/?#]+)/.exec(item.link || "");
    return m ? decodeURIComponent(m[1]) : null;
  }

  async _autoFix(key) {
    if (this._fixing) return;
    const item = (this._report?.findings || []).flatMap((f) => f.items || []).find((i) => i.key === key);
    if (!item) return;
    this._fixing = key;
    this._render();
    try {
      let before;
      const autoId = this._autoId(item);
      if (item.fix === "use_new" || item.fix === "remove_step") {
        if (!autoId) throw new Error(this._t("This automation lives in a YAML file. Open it to change it."));
        before = await this._hass.callApi("GET", `config/automation/config/${encodeURIComponent(autoId)}`);
      }
      const start = await this._hass.callWS({ type: "home_checkup/fix_automation_start", key, ...(before ? { before } : {}) });
      const fix = start.fix;
      if (item.fix === "use_new") {
        const after = swapEntity(before, fix.old, fix.new);
        await this._hass.callApi("POST", `config/automation/config/${encodeURIComponent(autoId)}`, after);
      } else if (item.fix === "remove_step") {
        await this._hass.callApi("POST", `config/automation/config/${encodeURIComponent(autoId)}`, fix.after);
      } else {
        await this._hass.callService("automation", "turn_off", { entity_id: item.id });
      }
      const result = await this._hass.callWS({ type: "home_checkup/fix_automation_finish", fix_id: fix.id });
      this._report = result.report;
      const text =
        result.fix.status !== "done"
          ? this._t("It did not fully change. You can undo it.")
          : item.fix === "use_new"
            ? this._t("Updated. A backup was made.")
            : item.fix === "remove_step"
              ? this._t("Step removed. A backup was made.")
              : this._t("Turned off. You can turn it on again.");
      this._say({ text, act: "fixundo", data: fix.id });
    } catch (err) {
      this._say({ text: err?.message || this._t("Something went wrong. Nothing was changed.") });
    }
    this._fixing = null;
    this._render();
  }

  // ---- choose another entity for a broken step ----------------------------------------------------------------

  /** Where Home Assistant keeps this automation or script, for its own editor API. Null when it is in YAML. */
  _ownerPath(item) {
    if ((item.id || "").startsWith("script.")) return `config/script/config/${encodeURIComponent(item.id.split(".")[1])}`;
    const autoId = this._autoId(item);
    return autoId ? `config/automation/config/${encodeURIComponent(autoId)}` : null;
  }

  _openChoose(key) {
    const item = (this._report?.findings || []).flatMap((f) => f.items || []).find((i) => i.key === key);
    if (!item?.choose || !item.old) return;
    // Plain words where we have them: the name the missing thing had, not its raw id.
    this._choose = { key, name: item.name, old: item.old, oldName: this._target(item) || item.old, q: "", busy: false };
    this._paintChoose();
  }

  _paintChoose() {
    if (this._choose) this._choose.paint = true;
    this._render();
    if (this._choose) this._choose.paint = false;
  }

  /** Entities of the same kind as the missing one, by name. */
  _candidates() {
    const c = this._choose;
    const domain = c.old.split(".")[0];
    const q = c.q.trim().toLowerCase();
    // The closest names come first: the ones that share words with the missing one ("bedroom", "alexa").
    const words = [...new Set(`${c.old.split(".")[1] || ""} ${c.oldName || ""}`.toLowerCase().split(/[^a-z0-9]+/).filter((w) => w.length >= 3))];
    return Object.entries(this._hass?.states || {})
      .filter(([id]) => id.startsWith(domain + ".") && id !== c.old)
      .map(([id, st]) => ({ id, name: String(st?.attributes?.friendly_name || id) }))
      .filter((e) => !q || e.name.toLowerCase().includes(q) || e.id.includes(q))
      .map((e) => ({ ...e, near: words.filter((w) => `${e.name} ${e.id}`.toLowerCase().includes(w)).length }))
      .sort((a, b) => b.near - a.near || a.name.localeCompare(b.name));
  }

  _chooseListHtml() {
    const all = this._candidates();
    const shown = all.slice(0, CHOOSE_SHOWN);
    if (!shown.length) return `<div class="stext">${esc(this._t("Nothing of the same kind was found."))}</div>`;
    const more = all.length > shown.length ? `<div class="stext">${esc(this._t("Showing the first {n}. Search to find more.", { n: shown.length }))}</div>` : "";
    return (
      shown
        .map(
          (e) =>
            `<button type="button" class="pick" data-act="choosepick" data-key="${esc(e.id)}" ${this._choose.busy ? "disabled" : ""}><span class="nm">${esc(e.name)}</span><span class="info">${esc(e.id)}</span></button>`,
        )
        .join("") + more
    );
  }

  _chooseHtml() {
    const c = this._choose;
    if (!c) return "";
    const title = this._t("Choose what this step should use");
    const text = this._t("{name} points to {old}, which no longer exists. Choose what it should use now. A backup is made first.", { name: c.name, old: c.oldName });
    return `<div class="scrim" data-act="chooseclose"></div>
      <div class="sheet choosesheet" role="dialog" aria-modal="true" aria-label="${esc(title)}">
        <div class="stitle">${esc(title)}</div>
        <div class="stext">${esc(text)}</div>
        <input class="choosesearch" type="search" data-choose="q" placeholder="${esc(this._t("Search"))}" aria-label="${esc(this._t("Search"))}" value="${esc(c.q)}" ${c.busy ? "disabled" : ""}>
        <div class="picks">${this._chooseListHtml()}</div>
        <div class="sbuttons"><button type="button" class="ghost" data-act="chooseclose" ${c.busy ? "disabled" : ""}>${esc(this._t("Cancel"))}</button></div>
      </div>`;
  }

  async _chooseFix(newId) {
    const c = this._choose;
    if (!c || c.busy) return;
    const item = (this._report?.findings || []).flatMap((f) => f.items || []).find((i) => i.key === c.key);
    if (!item) return;
    c.busy = true;
    this._paintChoose();
    let say;
    try {
      const path = this._ownerPath(item);
      const yaml = item.id.startsWith("script.")
        ? this._t("This script lives in a YAML file. Open it to change it.")
        : this._t("This automation lives in a YAML file. Open it to change it.");
      if (!path) throw new Error(yaml);
      let before;
      try {
        before = await this._hass.callApi("GET", path);
      } catch {
        throw new Error(yaml);
      }
      const start = await this._hass.callWS({ type: "home_checkup/fix_automation_start", key: c.key, before, new: newId });
      const fix = start.fix;
      await this._hass.callApi("POST", path, swapEntity(before, fix.old, fix.new));
      const result = await this._hass.callWS({ type: "home_checkup/fix_automation_finish", fix_id: fix.id });
      this._report = result.report;
      say = {
        text: result.fix.status !== "done" ? this._t("It did not fully change. You can undo it.") : this._t("Updated. A backup was made."),
        act: "fixundo",
        data: fix.id,
      };
    } catch (err) {
      say = { text: err?.message || this._t("Something went wrong. Nothing was changed.") };
    }
    this._choose = null;
    this._say(say);
    this._render();
  }

  async _undoFix(id) {
    const fix = (this._report?.fixes || []).find((f) => f.id === id);
    if (!fix || this._undoing) return;
    this._undoing = id;
    this._render();
    try {
      let result;
      if (fix.kind === "leftover_entities") {
        result = await this._hass.callWS({ type: "home_checkup/fix_undo", fix_id: id });
      } else if (["use_new", "remove_step", "turn_off", "choose"].includes(fix.kind)) {
        const saved = await this._hass.callWS({ type: "home_checkup/fix_automation_saved", fix_id: id });
        if (fix.kind === "turn_off") {
          await this._hass.callService("automation", "turn_on", { entity_id: saved.automation });
        } else if ((saved.automation || "").startsWith("script.") && saved.before) {
          await this._hass.callApi("POST", `config/script/config/${encodeURIComponent(saved.automation.split(".")[1])}`, saved.before);
        } else if (saved.before?.id) {
          await this._hass.callApi("POST", `config/automation/config/${encodeURIComponent(saved.before.id)}`, saved.before);
        }
        result = await this._hass.callWS({ type: "home_checkup/fix_automation_finish", fix_id: id, undo: true });
      } else {
        const saved = await this._hass.callWS({ type: "home_checkup/fix_helpers_saved", fix_id: id });
        for (const h of saved) {
          const { id: _old, ...fields } = h.item || {};
          try {
            await this._hass.callWS({ type: `${h.domain}/create`, ...fields });
          } catch {
            // counted below
          }
        }
        result = await this._hass.callWS({ type: "home_checkup/fix_helpers_finish", fix_id: id, undo: true });
      }
      this._report = result.report;
      this._say({ text: this._t("Undone. {n} brought back.", { n: result.fix.restored ?? 0 }) });
      this._scan(); // a fresh list right after an Undo
    } catch (err) {
      this._say({ text: err?.message || this._t("Something went wrong.") });
    }
    this._undoing = null;
    this._render();
  }

  // ---- ask for a fix ------------------------------------------------------------------------------------------

  /** Lines this browser already asked about, so the button says "Asked". Kept in the browser only. */
  _asked() {
    try {
      return JSON.parse(localStorage.getItem("home_checkup.asked") || "[]");
    } catch {
      return [];
    }
  }

  /** The code our server gave for each request, by line. Kept in the browser only. */
  _askCodes() {
    try {
      return JSON.parse(localStorage.getItem("home_checkup.askcodes") || "{}") || {};
    } catch {
      return {};
    }
  }

  /**
   * What happened to the requests of this browser: "planned" or "fixed in version X". The page sends only the
   * codes it got when the person pressed Send. Nothing about the home is sent. At most once every few hours.
   */
  async _checkNews() {
    if (this._newsAsked) return;
    this._newsAsked = true;
    const codes = [...new Set(Object.values(this._askCodes()))].filter((c) => /^[0-9a-f]{64}$/.test(c)).slice(-50);
    if (!codes.length) return;
    try {
      const saved = JSON.parse(localStorage.getItem("home_checkup.asknews") || "null");
      if (saved && typeof saved.status === "object") this._newsStatus = saved.status;
      if (saved && Date.now() - saved.at < NEWS_EVERY) return this._render();
    } catch {
      // no saved answer: ask
    }
    try {
      const res = await fetch(STATUS_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "omit",
        referrerPolicy: "no-referrer",
        body: JSON.stringify({ v: 1, codes }),
      });
      const reply = await res.json();
      if (!res.ok || !reply.ok || typeof reply.status !== "object") return;
      this._newsStatus = reply.status;
      try {
        localStorage.setItem("home_checkup.asknews", JSON.stringify({ at: Date.now(), status: reply.status }));
      } catch {
        // a private window: asked again next time
      }
      if (!this._ask) this._render();
    } catch {
      // offline or blocked: the page works the same without it
    }
  }

  /** The news for one line: { text } to show, and whether the person may ask again. */
  _news(key) {
    const news = (this._newsStatus || {})[this._askCodes()[key]];
    if (!news) return null;
    if (news.status === "planned") return { text: this._t("A fix is planned."), again: false };
    if (news.status !== "fixed") return null;
    // Fixed, but the version was not given: say so, and let the person ask again when the line is still here.
    if (!/^[0-9][0-9A-Za-z.\-+]{0,19}$/.test(news.fixed_in || "")) return { text: this._t("A fix arrived."), again: true };
    // The fix is in a version this home already has, and the line is still here: let the person ask again.
    if (!newerVersion(news.fixed_in, this._report?.version || "")) return { text: "", again: true };
    return { text: this._t("A fix arrived in version {version}. Update to get it.", { version: news.fixed_in }), again: false };
  }

  /** What would be sent for one line. No names of devices, people or places: only the kind of problem. */
  _openAsk(kind, key) {
    const finding = (this._report?.findings ?? []).find((f) => f.kind === kind && (f.items ?? []).some((it) => it.key === key));
    const it = finding?.items.find((i) => i.key === key);
    if (!it) return;
    let integration = finding.integration || "";
    let item = "";
    let text = it.name || "";
    if (kind === "broken_references") {
      const [, source = "", ...rest] = key.split(":");
      const target = rest.join(":");
      item = source.startsWith("script.") ? "script" : "automation";
      const what = target.startsWith("a removed device") ? "a removed device" : `a missing ${target.split(".")[0]}`;
      text = `A step points to ${what}.`;
    } else if (kind === "failed_integrations") {
      integration = (it.link || "").split("/integration/")[1] || "";
      text = it.info || "Did not start";
    }
    if (!/^[a-z0-9_]*$/.test(integration)) integration = "";
    this._ask = { key, kind, integration, item, text: text.slice(0, 600), note: "", email: "", busy: false, error: "", done: null };
    this._paintAsk();
  }

  _paintAsk() {
    if (this._ask) this._ask.paint = true;
    this._render();
    if (this._ask) this._ask.paint = false;
  }

  async _sendAsk() {
    const a = this._ask;
    if (!a || a.busy) return;
    a.busy = true;
    a.error = "";
    this._paintAsk();
    try {
      const res = await fetch(ASK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "omit",
        referrerPolicy: "no-referrer",
        body: JSON.stringify({
          v: 1,
          kind: a.kind,
          integration: a.integration,
          item: a.item,
          text: a.text.trim().slice(0, 600),
          note: a.note.trim().slice(0, 500),
          email: a.email.trim().slice(0, 200),
          hc: this._report?.version || "",
          ha: this._hass?.config?.version || "",
          lang: this._lang(),
        }),
      });
      const reply = await res.json().catch(() => ({}));
      if (!res.ok || !reply.ok) {
        a.error =
          res.status === 429
            ? this._t("Too many requests. Please try again in an hour.")
            : reply.error === "bad_email"
              ? this._t("The email address does not look right.")
              : this._t("Could not send. Please try again later.");
      } else {
        a.done = reply;
        try {
          localStorage.setItem("home_checkup.asked", JSON.stringify([...new Set([...this._asked(), a.key])].slice(-200)));
          if (/^[0-9a-f]{64}$/.test(reply.code || "")) {
            const codes = Object.entries({ ...this._askCodes(), [a.key]: reply.code }).slice(-200);
            localStorage.setItem("home_checkup.askcodes", JSON.stringify(Object.fromEntries(codes)));
          }
        } catch {
          // a private window: the button will simply offer to ask again
        }
      }
    } catch {
      a.error = this._t("Could not send. Please try again later.");
    }
    a.busy = false;
    this._paintAsk();
  }

  _askHtml() {
    const a = this._ask;
    if (!a) return "";
    const title = this._t("Ask for a fix");
    if (a.done) {
      const more =
        a.done.status === "fixed" && a.done.fixed_in
          ? this._t("Good news: this is fixed in version {version}.", { version: a.done.fixed_in })
          : a.done.status === "planned"
            ? this._t("A fix for this is already planned.")
            : this._t("We read every request and build the most wanted fixes first.");
      return `<div class="scrim" data-act="askclose"></div>
        <div class="sheet asksheet" role="dialog" aria-modal="true" aria-label="${esc(title)}">
          <div class="askdone">${mark("good")}<div><div class="stitle">${esc(this._t("Thank you. Your request was received."))}</div><div class="stext">${esc(more)}</div></div></div>
          <div class="sbuttons"><button type="button" class="send" data-act="askclose">${esc(this._t("Done"))}</button></div>
        </div>`;
    }
    const kindWords = this._tn(1, (TITLES[a.kind] ?? ["", ""])[0], (TITLES[a.kind] ?? ["", ""])[1]).replace(/^1\s+/, "");
    const what = a.kind === "log_errors" ? this._t("Log error") : kindWords.replace(/^./, (c) => c.toUpperCase());
    const facts = [
      [this._t("Problem"), what + (a.item ? ` · ${a.item}` : "")],
      a.integration ? [this._t("Integration"), a.integration] : null,
      [this._t("Versions"), `Home Checkup ${this._report?.version || "?"} · Home Assistant ${this._hass?.config?.version || "?"}`],
    ].filter(Boolean);
    return `<div class="scrim" data-act="askclose"></div>
      <div class="sheet asksheet" role="dialog" aria-modal="true" aria-label="${esc(title)}">
        <div class="stitle">${esc(title)}</div>
        <div class="stext">${esc(this._t("This goes to the makers of Home Checkup. Only what you see here is sent, and only when you press Send."))}</div>
        <dl class="askfacts">${facts.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join("")}</dl>
        <label class="asklabel" for="asktext">${esc(this._t("The error text. Remove anything you do not want to share."))}</label>
        <textarea id="asktext" data-ask="text" maxlength="600" rows="3" ${a.busy ? "disabled" : ""}>${esc(a.text)}</textarea>
        <label class="asklabel" for="asknote">${esc(this._t("Add a note (optional)"))}</label>
        <textarea id="asknote" data-ask="note" maxlength="500" rows="2" ${a.busy ? "disabled" : ""}>${esc(a.note)}</textarea>
        <label class="asklabel" for="askmail">${esc(this._t("Your email, only if you want an answer (optional)"))}</label>
        <input id="askmail" type="email" data-ask="email" maxlength="200" autocomplete="email" value="${esc(a.email)}" ${a.busy ? "disabled" : ""}>
        <div class="safe"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l7 3v5c0 4.5-3 8.3-7 9.5C8 19.3 5 15.5 5 11V6l7-3z"/></svg>${esc(this._t("No device names, no addresses and no account are sent."))}</div>
        ${a.error ? `<div class="serror">${esc(a.error)}</div>` : ""}
        <div class="sbuttons">
          <button type="button" class="ghost big" data-act="askclose" ${a.busy ? "disabled" : ""}>${esc(this._t("Cancel"))}</button>
          <button type="button" class="send" data-act="asksend" ${a.busy ? "disabled" : ""}>${esc(a.busy ? this._t("Sending…") : this._t("Send"))}</button>
        </div>
      </div>`;
  }

  _sheetHtml() {
    const s = this._sheet;
    if (!s) return "";
    const ready = s.items.filter((it) => it.ok);
    const on = ready.filter((it) => it.on).length;
    const title =
      s.kind === "leftover_entities" ? this._t("Remove leftover entities") : this._t("Remove helpers nothing uses");
    const text =
      s.kind === "leftover_entities"
        ? this._t("Nothing provides these any more. Untick any you want to keep.")
        : this._t("Pick only the ones you are sure about. Something outside Home Assistant, like Node-RED, may still use them.");
    const rows = s.items
      .map(
        (it, i) => `<li class="${it.ok ? "" : "off"}"><label>
          <input type="checkbox" data-act="tick" data-i="${i}" ${it.on ? "checked" : ""} ${it.ok && !s.busy ? "" : "disabled"}>
          <span class="what"><span class="nm">${esc(it.name)}</span><span class="info ${it.ok ? "code" : ""}">${esc(it.ok ? it.id : this._t("Made in YAML. Remove it from your YAML files."))}</span></span>
        </label></li>`,
      )
      .join("");
    return `<div class="scrim" data-act="sheetclose"></div>
      <div class="sheet" role="dialog" aria-modal="true" aria-label="${esc(title)}">
        <div class="stitle">${esc(title)}</div>
        <div class="stext">${esc(text)}</div>
        <div class="safe"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l7 3v5c0 4.5-3 8.3-7 9.5C8 19.3 5 15.5 5 11V6l7-3z"/></svg>${esc(this._t("A backup is made first. You can undo this for 30 days."))}</div>
        ${s.items.length > ready.length && s.kind !== "leftover_entities" ? `<div class="stext yamlnote">${esc(this._tn(s.items.length - ready.length, "{n} of these is written in a YAML file. The button cannot remove it.", "{n} of these are written in YAML files. The button cannot remove them."))}</div>` : ""}
        ${ready.length > 1 ? `<div class="allrow"><button type="button" class="link" data-act="tickall">${esc(on === ready.length ? this._t("Untick all") : this._t("Tick all"))}</button></div>` : ""}
        <ul class="pick">${rows || `<li class="off">${esc(s.busy ? "…" : this._t("Nothing to remove."))}</li>`}</ul>
        ${s.error ? `<div class="serror">${esc(s.error)}</div>` : ""}
        <div class="sbuttons">
          <button type="button" class="ghost big" data-act="sheetclose" ${s.busy && s.plan_id ? "disabled" : ""}>${esc(this._t("Cancel"))}</button>
          <button type="button" class="danger" data-act="runfix" ${on && !s.busy ? "" : "disabled"}>${esc(s.busy && s.plan_id ? this._t("Removing…") : (on ? this._t("Remove {n}", { n: on }) : this._t("Remove")))}</button>
        </div>
      </div>`;
  }

  _fixesHtml(fixes) {
    if (!fixes.length) return "";
    const rows = fixes
      .map((f) => {
        const when = this._when(f.at);
        const auto = f.items?.[0]?.name ?? "";
        const what =
          f.kind === "leftover_entities"
            ? this._tn(f.removed, "Removed {n} leftover entity", "Removed {n} leftover entities")
            : f.kind === "use_new" || f.kind === "choose"
              ? this._t("Updated {name}", { name: auto })
              : f.kind === "remove_step"
                ? this._t("Removed a step from {name}", { name: auto })
                : f.kind === "turn_off"
                ? this._t("Turned off {name}", { name: auto })
                : this._tn(f.removed, "Removed {n} helper", "Removed {n} helpers");
        const open = !f.undone_at && new Date(f.undo_until) > new Date();
        const side = f.undone_at
          ? `<span class="done">${esc(this._t("Undone"))}</span>`
          : open
            ? `<button type="button" class="ghost" data-act="fixundo" data-key="${esc(f.id)}" ${this._undoing ? "disabled" : ""}>${esc(this._undoing === f.id ? "…" : this._t("Undo"))}</button>`
            : "";
        return `<li><span class="what"><span class="nm">${esc(what)}</span><span class="info">${esc(when)}${f.status === "check" ? " · " + esc(this._t("Some did not change")) : ""}</span></span>${side}</li>`;
      })
      .join("");
    return `<div class="section">${esc(this._t("Recent fixes"))}</div><ul class="kept fixes">${rows}</ul>`;
  }

  _when(iso) {
    try {
      return new Date(iso).toLocaleString(this._hass?.locale?.language || undefined, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
    } catch {
      return "";
    }
  }

  _go(path) {
    if (!path) return;
    history.pushState(null, "", path);
    window.dispatchEvent(new CustomEvent("location-changed", { detail: { replace: false } }));
  }

  // ---- page --------------------------------------------------------------------------------------------------

  _render() {
    const root = this.shadowRoot;
    // While someone types in the "Ask for a fix" sheet, a background refresh must not wipe the words or the cursor.
    if (this._ask && !this._ask.paint && root.querySelector(".asksheet")) {
      this._ask.stale = true;
      return;
    }
    // The same for the list of choices: the search words and the place in the list stay.
    if (this._choose && !this._choose.paint && root.querySelector(".choosesheet")) {
      this._choose.stale = true;
      return;
    }
    if (!root.querySelector(".page")) {
      root.innerHTML = `<style>${STYLE}</style>
        <div class="page">
          <div class="toolbar">
            <span class="menu"></span>
            <div class="name"></div>
            <button class="scan" type="button"></button>
          </div>
          <div class="content"></div>
        </div>`;
      this._menu = document.createElement("ha-menu-button");
      this._menu.hass = this._hass;
      this._menu.narrow = this._narrow;
      root.querySelector(".menu").append(this._menu);
      root.querySelector(".scan").addEventListener("click", () => this._scan(true));
      root.querySelector(".content").addEventListener("click", (e) => this._click(e));
      root.querySelector(".content").addEventListener("change", (e) => this._click(e));
      root.querySelector(".content").addEventListener("input", (e) => {
        const field = e.target?.dataset?.ask;
        if (field && this._ask) this._ask[field] = e.target.value;
        if (e.target?.dataset?.choose === "q" && this._choose) {
          // Only the list is drawn again, so the cursor stays in the search box.
          this._choose.q = e.target.value;
          const picks = root.querySelector(".picks");
          if (picks) picks.innerHTML = this._chooseListHtml();
        }
      });
    }
    root.querySelector(".name").textContent = this._t("Home Checkup");
    const scan = root.querySelector(".scan");
    // Older Home Assistant has a top bar in the accent colour. An accent-coloured button would vanish on it.
    scan.classList.toggle("onbar", this._barIsAccent());
    scan.disabled = this._scanning || this._error === "not_loaded";
    scan.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true" class="${this._scanning ? "spin" : ""}"><path d="M17.65 6.35A7.96 7.96 0 0 0 12 4a8 8 0 1 0 7.73 10h-2.08A6 6 0 1 1 12 6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg><span>${esc(this._t(this._scanning ? "Checking…" : "Check now"))}</span>`;
    root.querySelector(".content").innerHTML = this._body();
  }

  _body() {
    if (this._error === "not_loaded") {
      return `<div class="hero off">${mark("off")}<div class="words"><div class="headline">${esc(this._t("Home Checkup is not set up."))}</div><div class="detail">${esc(this._t("Add it in Settings, Devices and services."))}</div></div></div>`;
    }
    if (this._error) {
      return `<div class="hero off">${mark("off")}<div class="words"><div class="headline">${esc(this._t("Could not load the report."))}</div></div></div>`;
    }
    const r = this._report;
    if (!r) return "";
    const findings = r.findings ?? [];
    // One number everywhere: the headline counts what the Repairs note and the sensor count. A short burst of log
    // errors (in_note false) is shown under "To watch" and does not raise the number.
    const warnings = findings.filter((f) => f.severity === "warning" && f.in_note !== false);
    const watch = findings.filter((f) => f.severity === "warning" && f.in_note === false);
    const notes = findings.filter((f) => f.severity !== "warning");
    const level = r.count ? "warn" : "good";
    const checked = r.scanned_at ? this._t("Checked {time}", { time: this._time(r.scanned_at) }) : this._t("Not checked yet");

    // The chips are a small menu: one with a problem shows how many and jumps to its card, a green one says what
    // was checked, so a green mark shows the work behind it.
    const chips = CHECKS.map(([label, kinds]) => {
      const mine = findings.filter((f) => kinds.includes(f.kind));
      const counted = mine.filter((f) => f.severity === "warning" && f.in_note !== false);
      const state = counted.length ? "warn" : mine.length ? "note" : "fine";
      const icon =
        state === "fine"
          ? `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>`
          : `<span class="dot"></span>`;
      const n = state === "warn" ? `<span class="chipn">${counted.length}</span>` : "";
      const on = state === "fine" && this._chip === label;
      return `<button type="button" class="chip ${state} ${on ? "on" : ""}" data-act="chip" data-key="${esc(label)}" data-kind="${esc(state === "fine" ? "" : mine[0].kind)}" aria-expanded="${on ? "true" : "false"}">${icon}${esc(this._t(label))}${n}</button>`;
    }).join("");
    const chipLine = this._chip && CHECKED[this._chip] ? this._checkedLine(this._chip, r) : "";

    const kept = r.kept ?? [];
    let html = `
      <div class="hero ${level}">
        ${mark(level)}
        <div class="words">
          <div class="headline">${esc(this._headline(r.count ?? 0))}</div>
          <div class="detail">${esc(r.count ? this._t("Nothing changes until you choose to.") : this._t("Nothing needs a look today."))}</div>
          ${watch.length ? `<div class="detail also">${esc(this._t("{n} to watch", { n: watch.length }))}</div>` : ""}
        </div>
        <div class="checked">${esc(checked)}</div>
      </div>
      <div class="chips">${chips}</div>${chipLine ? `<div class="chipline" role="status">${esc(chipLine)}</div>` : ""}`;
    if (findings.length) {
      // "Ask" is explained only when a line on the page offers it.
      const canAsk = findings.some((f) => ASK_KINDS.includes(f.kind) && (f.items ?? []).some((it) => !it.fix && !it.choose && !it.file));
      const askHint = canAsk ? ` ${this._t("Ask sends us a request for a fix. You read it first.")}` : "";
      html += `<div class="keephint">${esc(this._t("Ignore means this is fine. It will not show again.") + askHint)}</div>`;
    }
    if (warnings.length) html += `<div class="grid">${warnings.map((f) => this._finding(f, false)).join("")}</div>`;
    if (watch.length) {
      html += `<div class="section">${esc(this._t("To watch"))}</div><div class="keephint">${esc(this._t("Seen only briefly. These count when they keep coming back."))}</div><div class="grid">${watch.map((f) => this._finding(f, false)).join("")}</div>`;
    }
    if (notes.length) {
      html += `<div class="section">${esc(this._t("Good to know"))}</div><div class="grid">${notes.map((f) => this._finding(f, true)).join("")}</div>`;
    }
    html += this._fixesHtml(r.fixes ?? []);
    if (kept.length) {
      html += `<button class="keptbar" type="button" data-act="kept">${esc(this._t("Ignored items ({n})", { n: kept.length }))}<svg viewBox="0 0 24 24" class="${this._keptOpen ? "up" : ""}" aria-hidden="true"><path d="M7 10l5 5 5-5"/></svg></button>`;
      if (this._keptOpen) {
        html += `<ul class="kept">${kept
          .map((k) => `<li><span class="nm">${esc(this._keptName(k))}</span><button type="button" class="ghost" data-act="unkeep" data-key="${esc(k)}">${esc(this._t("Show again"))}</button></li>`)
          .join("")}</ul>`;
      }
    }
    html += `<div class="foot">${esc(this._t("Home Checkup never changes anything by itself. A fix happens only when you tap it."))}</div>`;
    if (this._toast) {
      const t = this._toast;
      html += `<div class="toast" role="status">${esc(t.text)}${t.act ? `<button type="button" data-act="${t.act}" data-key="${esc(t.data)}">${esc(this._t("Undo"))}</button>` : ""}</div>`;
    }
    html += this._sheetHtml();
    html += this._askHtml();
    html += this._chooseHtml();
    return html;
  }

  /** What stands behind a green chip: how much was checked, and the result. */
  _checkedLine(label, r) {
    const c = r.checked ?? {};
    if (label === "Helpers" && r.helpers_checked === false) return this._t("Helpers are checked with the next full check.");
    const [text, ...keys] = CHECKED[label];
    if (keys.some((k) => c[k] === undefined)) return "";
    return this._t(text, Object.fromEntries(keys.map((k, i) => [["n", "m"][i], c[k]])));
  }

  _finding(f, note) {
    const items = f.items ?? [];
    const id = `${f.kind}:${f.integration ?? ""}`;
    const open = this._open.has(id);
    const shown = open ? items : items.slice(0, SHOWN);
    const isLog = f.kind === "log_errors" || f.kind === "log_warnings";
    const rows = shown
      .map((it) => {
        const target = this._target(it);
        const pill = it.new ? `<span class="newpill">${esc(this._t("New"))}</span>` : "";
        const name = `<span class="nm">${pill}${esc(it.name)}${target ? `<span class="to"> · ${esc(target)}</span>` : ""}</span>`;
        const tryText = it.hint && TRY[it.hint] ? `<span class="try">${esc(this._t("Try: {text}", { text: this._t(TRY[it.hint]) }))}</span>` : "";
        const mean = it.hint && MEANINGS[it.hint] ? `<span class="mean">${esc(this._t(MEANINGS[it.hint]))}</span>${tryText}` : "";
        let infoText = it.info;
        if (f.kind === "broken_references") {
          // Plain words, no raw ids: what happened to the missing thing, then when the automation last ran.
          const why =
            it.fix === "use_new"
              ? this._t("Renamed to {name}", { name: it.to_name })
              : it.gone
                ? this._t("{name} was removed", { name: it.gone })
                : it.fix === "turn_off"
                  ? this._t("Its device was removed")
                  : this._t("No longer exists");
          infoText = `${why} · ${this._lastRan(it.last_ran)}`;
        }
        const news = this._asked().includes(it.key) ? this._news(it.key) : null;
        const newsLine = news?.text ? `<span class="fixnews">${esc(news.text)}</span>` : "";
        // Written by hand in a YAML file: no button can change it, so the line says where to look.
        const where = it.file
          ? `<span class="mean">${esc(this._t("Written in {file}, line {line}. Change it in that file.", { file: it.file, line: it.line }))}</span>`
          : "";
        const info = (infoText ? `<span class="info">${esc(infoText)}</span>` : "") + mean + where + newsLine;
        // A log line opens in place and shows the full error, so nobody has to search the whole log for it.
        const detail = isLog ? this._details[it.key] : null;
        const label = isLog
          ? `<button type="button" class="what detailbtn" data-act="detail" data-key="${esc(it.key)}" aria-expanded="${detail ? "true" : "false"}" title="${esc(this._t("Show the full error"))}">${name}${info}</button>`
          : it.link
            ? `<a class="what" href="${esc(it.link)}" data-act="go" data-link="${esc(it.link)}">${name}${info}</a>`
            : `<span class="what">${name}${info}</span>`;
        const chevron = isLog
          ? `<button type="button" class="chev ${detail ? "on" : ""}" data-act="detail" data-key="${esc(it.key)}" aria-label="${esc(this._t("Show the full error"))}"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="m9 6 6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>`
          : "";
        const detailBox = detail ? this._detailHtml(it.key, detail) : "";
        const fixLabel = it.fix === "use_new" ? "Use the new one" : it.fix === "remove_step" ? "Remove this step" : it.fix === "turn_off" ? "Turn off" : "";
        const fixBtn = fixLabel
          ? `<button type="button" class="fixbtn" data-act="autofix" data-key="${esc(it.key)}" ${this._fixing ? "disabled" : ""}>${esc(this._fixing === it.key ? "…" : this._t(fixLabel))}</button>`
          : "";
        // No safe fix for this line yet: the person can ask us for one. Nothing is sent before they read it and press Send.
        // No fix by itself, but the person can choose what the step should use now.
        const chooseBtn =
          !fixBtn && it.choose
            ? `<button type="button" class="fixbtn" data-act="choose" data-key="${esc(it.key)}" ${this._fixing ? "disabled" : ""}>${esc(this._t("Choose another"))}</button>`
            : "";
        const askBtn =
          !fixBtn && !chooseBtn && !it.file && ASK_KINDS.includes(f.kind)
            ? this._asked().includes(it.key) && !news?.again
              ? `<span class="asked">${esc(this._t("Asked"))}</span>`
              : `<button type="button" class="ghost ask" data-act="ask" data-kind="${esc(f.kind)}" data-key="${esc(it.key)}">${esc(this._t("Ask"))}</button>`
            : "";
        return `<li class="${fixBtn || chooseBtn || askBtn ? "hasfix" : ""}${detail ? " hasdetail" : ""}">${chevron ? `<span class="lw">${chevron}${label}</span>` : label}<span class="rowacts">${fixBtn}${chooseBtn}${askBtn}<button type="button" class="ghost" data-act="keep" data-key="${esc(it.key)}">${esc(this._t("Ignore"))}</button></span>${detailBox}</li>`;
      })
      .join("");
    const more =
      items.length > SHOWN
        ? `<button type="button" class="more" data-act="more" data-id="${esc(id)}">${esc(open ? this._t("Show fewer") : this._t("Show all {n}", { n: items.length }))}</button>`
        : "";
    const step = STEPS[f.action];
    let openLink = f.link
      ? `<a class="open" href="${esc(f.link)}" data-act="go" data-link="${esc(f.link)}">${esc(this._t(placeName(f.link)))}${ARROW}</a>`
      : "";
    if (step && f.kind === "log_errors") {
      const label = f.action === "template" && !f.action_link.startsWith("/config/lovelace") ? placeName(f.action_link) : step[1];
      openLink = `<a class="open stepbtn" href="${esc(f.action_link)}" data-act="step" data-link="${esc(f.action_link)}" data-key="${esc(f.integration ?? "")}" data-step="${esc(f.action)}">${esc(this._t(label))}${ARROW}</a>`;
    }
    let hint = this._t(HINTS[f.kind] ?? "");
    if (f.kind === "log_stopped") hint = this._t(STOPPED[f.action] ?? "No errors since you took the next step.");
    else if (f.kind === "log_errors" && f.severity === "info") hint = this._t("Only right after a restart. Usually harmless, but it hides real errors.");
    // Only an update is news the lines below do not already say; then it takes the place of the grey hint.
    const stepLine =
      f.action === "update" && f.kind === "log_errors" ? `<div class="step">${esc(this._t(step[0], { version: f.action_info }))}</div>` : "";
    if (stepLine) hint = "";
    const fixButton =
      f.kind === "leftover_entities" || f.kind === "unused_helpers"
        ? `<button type="button" class="fixbtn" data-act="fix" data-key="${esc(f.kind)}">${esc(this._t("Remove…"))}</button>`
        : "";
    return `
      <section class="finding ${note ? "note" : ""}" data-kind="${esc(f.kind)}">
        <div class="head">
          <div class="htext"><div class="title">${esc(this._title(f))}</div>${hint ? `<div class="hint">${esc(hint)}</div>` : ""}</div>
          <div class="acts">${fixButton}${openLink}</div>
        </div>
        ${stepLine}
        ${rows && f.kind !== "log_stopped" ? `<ul class="${isLog ? "log" : ""}">${rows}</ul>` : ""}
        ${more}
      </section>`;
  }

  /** The full error of one log line, read only when the person opens it. It stays in the home. */
  async _toggleDetail(key) {
    if (this._details[key]) {
      delete this._details[key];
      return this._render();
    }
    const d = (this._details[key] = { data: null, error: "", all: false, copied: false });
    this._render();
    try {
      d.data = await this._hass.callWS({ type: "home_checkup/log_detail", key });
    } catch {
      d.error = this._t("Could not read the full error.");
    }
    if (this._details[key] === d) this._render();
  }

  _detailHtml(key, d) {
    if (d.error) return `<div class="errdetail"><div class="dmeta">${esc(d.error)}</div></div>`;
    if (!d.data) return `<div class="errdetail"><div class="dmeta">…</div></div>`;
    const lines = String(d.data.text || "").split("\n");
    // A long error keeps its first lines (what was tried) and its last lines (what went wrong): the end says the most.
    const short = !d.all && lines.length > DETAIL_LINES;
    const text = (short ? [...lines.slice(0, 3), "…", ...lines.slice(3 - DETAIL_LINES)] : lines).join("\n");
    const x = d.data;
    const from = [x.logger, x.source].filter(Boolean).join(" · ");
    const at = (t) => this._when(new Date(t * 1000).toISOString());
    // The facts a person who troubleshoots looks for first, in one quiet line.
    const facts = [
      x.integration ? this._t(x.likely ? "Likely from {name}" : "{name}", { name: x.integration }) + (x.version ? ` ${x.version}` : "") : "",
      x.first ? this._t("First seen {when}", { when: at(x.first) }) : "",
      x.last ? this._t("Last seen {when}", { when: at(x.last) }) : "",
      x.count ? this._t("{n} times in 24 hours", { n: x.count }) : "",
    ].filter(Boolean).join(" · ");
    const links = [
      x.issues ? `<a class="dlink" href="${esc(x.issues)}" target="_blank" rel="noopener noreferrer">${esc(this._t("Known issues"))}${ARROW}</a>` : "",
      x.page ? `<a class="dlink" href="${esc(x.page)}" data-act="go" data-link="${esc(x.page)}" title="${esc(this._t("The integration page has the debug logging switch."))}">${esc(this._t("Debug logging"))}${ARROW}</a>` : "",
    ].join("");
    return `<div class="errdetail">
      ${facts ? `<div class="dmeta">${esc(facts)}</div>` : ""}
      ${from ? `<div class="dmeta code">${esc(from)}</div>` : ""}
      <pre class="dtext">${esc(text)}</pre>
      <div class="dacts">
        <span class="dlinks">${links}</span>
        ${short ? `<button type="button" class="ghost" data-act="detailall" data-key="${esc(key)}">${esc(this._t("Show all lines"))}</button>` : ""}
        <button type="button" class="ghost" data-act="detailcopy" data-key="${esc(key)}" title="${esc(this._t("Copies a report you can paste into a bug report."))}">${esc(this._t(d.copied ? "Copied" : "Copy"))}</button>
      </div>
    </div>`;
  }

  /** Copies the error with the few facts a forum or a GitHub report asks for. No names of devices or people. */
  async _copyDetail(key) {
    const d = this._details[key];
    if (!d?.data) return;
    const text = [
      `Home Assistant ${this._hass?.config?.version || ""}`.trim(),
      d.data.integration ? `${d.data.likely ? "Likely from: " : "Integration: "}${d.data.integration}${d.data.version ? ` ${d.data.version}` : ""}` : "",
      [d.data.logger, d.data.source].filter(Boolean).join(" · "),
      `${d.data.level || "ERROR"}, ${d.data.count || 1}x in 24 h, last ${new Date((d.data.last || 0) * 1000).toISOString()}`,
      "",
      "```",
      d.data.text || "",
      "```",
    ]
      .filter((line, i) => line || i > 1)
      .join("\n");
    let ok = false;
    try {
      await navigator.clipboard.writeText(text);
      ok = true;
    } catch {
      // Home Assistant opened over plain http has no clipboard API: use the old way.
      const area = document.createElement("textarea");
      area.value = text;
      area.setAttribute("readonly", "");
      area.style.cssText = "position:fixed;opacity:0;top:0;left:0";
      this.shadowRoot.appendChild(area);
      area.select();
      try {
        ok = document.execCommand("copy");
      } catch {
        ok = false;
      }
      area.remove();
    }
    if (!ok) return;
    d.copied = true;
    this._render();
    setTimeout(() => {
      if (this._details[key] === d) {
        d.copied = false;
        this._render();
      }
    }, 2500);
  }

  _click(e) {
    const el = e.target.closest("[data-act]");
    if (!el) return;
    const act = el.dataset.act;
    if (act === "go") {
      e.preventDefault();
      this._go(el.dataset.link);
    } else if (act === "step") {
      // Remember the next step, so Home Checkup can say later if the errors stopped. Then go there.
      e.preventDefault();
      this._hass.callWS({ type: "home_checkup/acted", integration: el.dataset.key, action: el.dataset.step }).catch(() => {});
      this._go(el.dataset.link);
    } else if (act === "detail") {
      this._toggleDetail(el.dataset.key);
    } else if (act === "chip") {
      const kind = el.dataset.kind;
      if (kind) {
        // A chip with a problem jumps to its first card.
        this._chip = "";
        this._render();
        const card = this.shadowRoot.querySelector(`section.finding[data-kind="${kind}"]`);
        card?.scrollIntoView({ behavior: "smooth", block: "start" });
        card?.classList.add("flash");
        setTimeout(() => card?.classList.remove("flash"), 1200);
      } else {
        this._chip = this._chip === el.dataset.key ? "" : el.dataset.key;
        this._render();
      }
    } else if (act === "detailall") {
      if (this._details[el.dataset.key]) this._details[el.dataset.key].all = true;
      this._render();
    } else if (act === "detailcopy") {
      this._copyDetail(el.dataset.key);
    } else if (act === "keep") {
      this._keep(el.dataset.key, true);
    } else if (act === "unkeep" || act === "undo") {
      this._keep(el.dataset.key, false);
    } else if (act === "more") {
      const id = el.dataset.id;
      this._open.has(id) ? this._open.delete(id) : this._open.add(id);
      this._render();
    } else if (act === "kept") {
      this._keptOpen = !this._keptOpen;
      this._render();
    } else if (act === "fix") {
      this._openFix(el.dataset.key);
    } else if (act === "sheetclose") {
      if (!(this._sheet?.busy && this._sheet?.plan_id)) {
        this._sheet = null;
        this._render();
      }
    } else if (act === "tick") {
      const it = this._sheet?.items[Number(el.dataset.i)];
      if (it) it.on = el.checked;
      this._render();
    } else if (act === "tickall") {
      const ready = this._sheet.items.filter((it) => it.ok);
      const all = ready.every((it) => it.on);
      ready.forEach((it) => (it.on = !all));
      this._render();
    } else if (act === "ask") {
      this._openAsk(el.dataset.kind, el.dataset.key);
    } else if (act === "askclose") {
      if (!this._ask?.busy) {
        const stale = this._ask?.stale;
        this._ask = null;
        stale ? this._load() : this._render();
      }
    } else if (act === "choose") {
      this._openChoose(el.dataset.key);
    } else if (act === "chooseclose") {
      if (!this._choose?.busy) {
        const stale = this._choose?.stale;
        this._choose = null;
        stale ? this._load() : this._render();
      }
    } else if (act === "choosepick") {
      this._chooseFix(el.dataset.key);
    } else if (act === "asksend") {
      this._sendAsk();
    } else if (act === "runfix") {
      this._runFix();
    } else if (act === "autofix") {
      this._autoFix(el.dataset.key);
    } else if (act === "fixundo") {
      this._toast = null;
      this._undoFix(el.dataset.key);
    }
  }
}

const STYLE = `
  :host { display: block; height: 100%; background: var(--primary-background-color); color: var(--primary-text-color);
    font-family: var(--ha-font-family-body, var(--paper-font-body1_-_font-family, system-ui, sans-serif));
    --good: var(--success-color, #43a047); --warn: var(--warning-color, #ffa600); --dim: var(--secondary-text-color);
    --card: var(--card-background-color, #fff); --line: var(--divider-color, rgba(127,127,127,.2)); }
  .page { height: 100%; display: flex; flex-direction: column; }
  .toolbar { height: var(--header-height, 56px); display: flex; align-items: center; gap: 4px; padding: 0 12px 0 4px; flex: none;
    background: var(--app-header-background-color, var(--primary-background-color)); color: var(--app-header-text-color, var(--primary-text-color));
    border-bottom: var(--app-header-border-bottom, none); }
  .menu { display: flex; }
  .name { flex: 1; font-size: 20px; font-weight: 400; padding-left: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .scan { display: inline-flex; align-items: center; gap: 8px; height: 36px; padding: 0 16px 0 12px; border: 0; border-radius: 18px; cursor: pointer;
    font: inherit; font-size: 14px; font-weight: 500; color: var(--primary-color); background: transparent; }
  .scan:hover { background: color-mix(in srgb, var(--primary-color) 10%, transparent); }
  .scan.onbar { color: var(--app-header-text-color, #fff); }
  .scan.onbar:hover { background: color-mix(in srgb, currentColor 14%, transparent); }
  .scan:disabled { opacity: .6; cursor: default; }
  .scan svg { width: 20px; height: 20px; fill: currentColor; }
  .spin { animation: spin 1s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .content { flex: 1; overflow-y: auto; padding: 24px 24px 48px; box-sizing: border-box; width: 100%; max-width: 948px; margin: 0 auto;
    display: flex; flex-direction: column; gap: 16px; }

  .hero { display: flex; align-items: center; gap: 20px; padding: 22px 24px; border-radius: var(--ha-card-border-radius, 12px); }
  .hero.good { background: color-mix(in srgb, var(--good) 12%, var(--card)); }
  .hero.warn { background: color-mix(in srgb, var(--warn) 14%, var(--card)); }
  .hero.off { background: var(--card); }
  .mark { width: 56px; height: 56px; flex: none; fill: none; stroke-width: 3; stroke-linecap: round; stroke-linejoin: round; }
  .mark.good { stroke: var(--good); } .mark.warn { stroke: var(--warn); }
  .mark.off { stroke: var(--dim); } .mark.off circle { stroke-dasharray: 4 5; }
  .words { flex: 1; min-width: 0; }
  .headline { font-size: 26px; font-weight: 600; letter-spacing: -0.01em; line-height: 1.2; }
  .detail { font-size: 15px; color: var(--dim); margin-top: 4px; }
  .checked { font-size: 13px; color: var(--dim); white-space: nowrap; align-self: flex-start; }

  .chips { display: flex; flex-wrap: wrap; gap: 8px; }
  .chip { display: inline-flex; align-items: center; gap: 8px; padding: 7px 14px 7px 9px; border-radius: 999px; font-size: 14px;
    background: var(--card); border: 1px solid var(--line); }
  .chip svg { width: 18px; height: 18px; padding: 2px; border-radius: 50%; box-sizing: border-box; fill: none; stroke: var(--good); stroke-width: 3;
    stroke-linecap: round; stroke-linejoin: round; background: color-mix(in srgb, var(--good) 18%, transparent); }
  .chip .dot { width: 10px; height: 10px; margin: 0 4px; border-radius: 50%; background: var(--warn); }
  .chip.note .dot { background: var(--dim); }
  .chip.warn { border-color: color-mix(in srgb, var(--warn) 50%, transparent); }
  button.chip { font: inherit; font-size: 14px; color: inherit; cursor: pointer; }
  button.chip:focus-visible { outline: 2px solid var(--primary-color); outline-offset: 2px; }
  .chip.on { border-color: color-mix(in srgb, var(--good) 55%, transparent); }
  .chipn { min-width: 20px; padding: 0 6px; margin-left: -2px; border-radius: 999px; box-sizing: border-box; text-align: center; font-size: 13px; font-weight: 600;
    color: var(--warn); background: color-mix(in srgb, var(--warn) 16%, transparent); }
  .chipline { margin-top: -6px; font-size: 14px; color: var(--dim); }
  section.finding { scroll-margin-top: 12px; }
  section.finding.flash { box-shadow: 0 0 0 2px color-mix(in srgb, var(--warn) 60%, transparent); transition: box-shadow 0.3s; }
  .keephint { font-size: 13px; color: var(--dim); }

  /* One card under the other: the page reads top to bottom, with no holes beside a tall card. */
  .grid { display: grid; grid-template-columns: minmax(0, 1fr); gap: 16px; align-items: start; }
  .finding { background: var(--card); border-radius: var(--ha-card-border-radius, 12px); padding: 16px 16px 10px 18px;
    box-shadow: inset 4px 0 0 var(--warn), var(--ha-card-box-shadow, none); border: var(--ha-card-border-width, 1px) solid var(--ha-card-border-color, var(--line)); }
  .finding.note { box-shadow: var(--ha-card-box-shadow, none); }
  .head { display: flex; gap: 12px; align-items: flex-start; }
  .head > .htext { flex: 1; min-width: 0; }
  .title { font-size: 17px; font-weight: 600; line-height: 1.25; }
  .hint { font-size: 14px; color: var(--dim); margin-top: 2px; }
  .acts { display: flex; align-items: center; gap: 4px; flex: none; }
  .fixbtn { height: 30px; padding: 0 12px; border-radius: 15px; border: 1px solid var(--line); background: transparent; color: var(--primary-text-color);
    font: inherit; font-size: 13px; font-weight: 500; cursor: pointer; }
  .fixbtn:hover { border-color: var(--dim); }
  .rowacts { display: flex; align-items: center; gap: 6px; flex: none; }
  li .fixbtn { color: var(--primary-color); border-color: color-mix(in srgb, var(--primary-color) 40%, transparent); }
  .open { font-size: 14px; font-weight: 500; color: var(--primary-color); text-decoration: none; padding: 4px 2px; white-space: nowrap; display: inline-flex; align-items: center; gap: 3px; }
  .open .arrow { flex: none; opacity: 0.85; }
  ul { list-style: none; margin: 10px 0 0; padding: 0; }
  li { display: flex; align-items: center; gap: 8px; padding: 6px 0; border-top: 1px solid var(--line); min-height: 36px; }
  .what { flex: 1; min-width: 0; display: flex; flex-direction: column; color: inherit; text-decoration: none; font-size: 15px; }
  a.what:hover .nm { color: var(--primary-color); }
  .nm { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .to, .info { color: var(--dim); }
  button.what { background: none; border: 0; padding: 0; margin: 0; font: inherit; text-align: left; cursor: pointer; align-items: stretch; }
  button.what:hover .nm { color: var(--primary-color); }
  .chev { flex: none; width: 26px; height: 24px; margin-left: -6px; padding: 0; border: 0; background: none; color: var(--dim); cursor: pointer; display: grid; place-items: center; }
  .chev svg { transition: transform 0.15s ease; }
  .chev.on { color: var(--primary-color); }
  .chev.on svg { transform: rotate(90deg); }
  li.hasdetail { flex-wrap: wrap; }
  .lw { flex: 1; min-width: 0; display: flex; align-items: flex-start; gap: 2px; }
  .lw .what { flex: 1; }
  .errdetail { flex-basis: 100%; min-width: 0; margin: 4px 0 6px; padding: 10px 12px; border-radius: 10px; background: color-mix(in srgb, var(--primary-text-color) 6%, transparent); }
  .dmeta { font-size: 12px; color: var(--dim); overflow-wrap: anywhere; }
  .dmeta.code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
  .dtext { margin: 8px 0; font: 12px/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; white-space: pre-wrap; overflow-wrap: anywhere; color: var(--primary-text-color); max-height: 60vh; overflow: auto; }
  .dacts { display: flex; gap: 6px; justify-content: flex-end; align-items: center; flex-wrap: wrap; }
  .dlinks { margin-right: auto; display: flex; gap: 14px; flex-wrap: wrap; }
  .dlink { display: inline-flex; align-items: center; gap: 3px; font-size: 13px; color: var(--primary-color); text-decoration: none; min-height: 32px; }
  .info { font-size: 13px; }
  .fixnews { display: block; font-size: 13px; color: var(--good); margin-top: 2px; }
  .mean { font-size: 13px; color: var(--primary-text-color); margin-top: 2px; }
  .try { font-size: 13px; color: var(--dim); margin-top: 1px; }
  .step { font-size: 14px; color: var(--primary-text-color); margin: -2px 0 2px; }
  .newpill { display: inline-block; vertical-align: 1px; margin-right: 6px; padding: 1px 7px; border-radius: 8px; font-size: 11px; font-weight: 700;
    letter-spacing: .03em; text-transform: uppercase; color: var(--primary-color); background: color-mix(in srgb, var(--primary-color) 16%, transparent); }
  ul.log .nm { white-space: normal; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; font-size: 14px; }
  .ghost { flex: none; height: 30px; padding: 0 12px; border-radius: 15px; border: 1px solid var(--line); background: transparent; color: var(--dim);
    font: inherit; font-size: 13px; cursor: pointer; }
  .ghost:hover { color: var(--primary-text-color); border-color: var(--dim); }
  .more { display: block; margin: 4px 0 2px; padding: 6px 0; border: 0; background: none; color: var(--primary-color); font: inherit; font-size: 14px; cursor: pointer; }
  .section { margin-top: 8px; text-transform: uppercase; letter-spacing: .06em; font-size: 12px; font-weight: 600; color: var(--dim); }
  .keptbar { align-self: flex-start; display: inline-flex; align-items: center; gap: 6px; margin-top: 8px; padding: 6px 0; border: 0; background: none;
    color: var(--dim); font: inherit; font-size: 14px; cursor: pointer; }
  .keptbar svg { width: 20px; height: 20px; fill: none; stroke: currentColor; stroke-width: 2; transition: transform .2s; }
  .keptbar svg.up { transform: rotate(180deg); }
  ul.kept { margin: 0; background: var(--card); border-radius: var(--ha-card-border-radius, 12px); padding: 4px 16px; }
  ul.kept li:first-child { border-top: 0; }
  ul.kept .nm { flex: 1; font-size: 15px; }
  .foot { margin-top: 12px; font-size: 13px; color: var(--dim); }
  .toast { position: fixed; left: 50%; bottom: 24px; transform: translateX(-50%); display: flex; align-items: center; gap: 16px;
    padding: 10px 10px 10px 18px; border-radius: 8px; background: var(--primary-text-color); color: var(--primary-background-color);
    font-size: 14px; box-shadow: 0 4px 16px rgba(0,0,0,.25); width: max-content; max-width: calc(100% - 32px); box-sizing: border-box; }
  .toast button { border: 0; background: none; color: var(--primary-color); font: inherit; font-weight: 600; cursor: pointer; padding: 6px 8px; }

  ul.fixes .done { color: var(--dim); font-size: 13px; padding: 0 6px; }
  .scrim { position: fixed; inset: 0; background: rgba(0,0,0,.45); z-index: 4; }
  .sheet { position: fixed; z-index: 5; left: 50%; top: 50%; transform: translate(-50%, -50%); width: min(560px, calc(100% - 32px));
    max-height: calc(100% - 48px); display: flex; flex-direction: column; box-sizing: border-box; padding: 22px 22px 16px;
    border-radius: 16px; background: var(--card); color: var(--primary-text-color); box-shadow: 0 12px 40px rgba(0,0,0,.35); }
  .stitle { font-size: 20px; font-weight: 600; }
  .stext { font-size: 14px; color: var(--dim); margin-top: 6px; }
  .safe { display: flex; align-items: center; gap: 8px; margin-top: 12px; font-size: 13px; color: var(--primary-text-color); }
  .safe svg { width: 18px; height: 18px; flex: none; fill: none; stroke: var(--good); stroke-width: 2; stroke-linejoin: round; }
  .allrow { margin-top: 8px; }
  .link { border: 0; background: none; padding: 4px 0; color: var(--primary-color); font: inherit; font-size: 14px; cursor: pointer; }
  ul.pick { flex: 1; min-height: 60px; overflow-y: auto; margin: 6px 0 0; }
  ul.pick label { display: flex; align-items: center; gap: 12px; width: 100%; cursor: pointer; }
  ul.pick input { width: 18px; height: 18px; flex: none; accent-color: var(--primary-color); }
  ul.pick li.off { opacity: .55; }
  ul.pick .info.code { font-family: var(--ha-font-family-code, ui-monospace, monospace); font-size: 12px; }
  .asksheet { max-height: calc(100% - 32px); overflow-y: auto; }
  .choosesheet { max-height: calc(100% - 32px); display: flex; flex-direction: column; }
  .choosesearch { width: 100%; box-sizing: border-box; margin-top: 14px; padding: 9px 11px; border-radius: 10px; border: 1px solid var(--line);
    background: var(--card); color: inherit; font: inherit; font-size: 15px; }
  .choosesearch:focus { outline: 2px solid color-mix(in srgb, var(--primary-color) 60%, transparent); outline-offset: 1px; }
  .picks { overflow-y: auto; margin-top: 8px; min-height: 80px; display: flex; flex-direction: column; gap: 2px; }
  .pick { display: flex; flex: none; flex-direction: column; align-items: flex-start; gap: 2px; width: 100%; box-sizing: border-box; text-align: left;
    padding: 9px 11px; min-height: 48px; line-height: 1.3;
    border: 0; border-radius: 10px; background: transparent; color: inherit; font: inherit; font-size: 15px; cursor: pointer; }
  .pick:hover, .pick:focus-visible { background: color-mix(in srgb, var(--primary-color) 12%, transparent); outline: none; }
  .pick .nm, .pick .info { display: block; max-width: 100%; overflow-wrap: anywhere; }
  .choosesheet .stitle, .choosesheet .stext, .choosesearch, .choosesheet .sbuttons { flex: none; }
  .askfacts { display: grid; grid-template-columns: auto 1fr; gap: 4px 14px; margin: 14px 0 0; font-size: 14px; }
  .askfacts dt { color: var(--dim); }
  .askfacts dd { margin: 0; overflow-wrap: anywhere; }
  .asklabel { display: block; margin: 14px 0 6px; font-size: 13px; color: var(--dim); }
  .asksheet textarea, .asksheet input { width: 100%; box-sizing: border-box; padding: 9px 11px; border-radius: 10px; border: 1px solid var(--line);
    background: var(--primary-background-color); color: var(--primary-text-color); font: inherit; font-size: 14px; resize: vertical; }
  .asksheet textarea:focus, .asksheet input:focus { outline: 2px solid color-mix(in srgb, var(--primary-color) 60%, transparent); outline-offset: 1px; }
  .askdone { display: flex; align-items: center; gap: 16px; }
  .askdone > svg, .askdone > .mark { width: 52px; height: 52px; flex: none; }
  .send { height: 36px; padding: 0 20px; border-radius: 18px; border: 0; background: var(--primary-color); color: var(--text-primary-color, #fff);
    font: inherit; font-size: 14px; font-weight: 500; cursor: pointer; }
  .send:disabled { opacity: .45; cursor: default; }
  .ghost.ask { color: var(--primary-text-color); }
  .asked { font-size: 13px; color: var(--dim); padding: 0 6px; white-space: nowrap; }
  .serror { margin-top: 10px; font-size: 14px; color: var(--error-color, #db4437); }
  .sbuttons { display: flex; justify-content: flex-end; gap: 10px; margin-top: 16px; }
  .ghost.big { height: 36px; padding: 0 16px; border-radius: 18px; font-size: 14px; }
  .danger { height: 36px; padding: 0 18px; border-radius: 18px; border: 0; background: var(--error-color, #db4437); color: #fff;
    font: inherit; font-size: 14px; font-weight: 600; cursor: pointer; }
  .danger:disabled, .ghost:disabled { opacity: .45; cursor: default; }

  @media (max-width: 600px) {
    .content { padding: 16px 16px 40px; gap: 14px; }
    .hero { padding: 18px; gap: 14px; flex-wrap: wrap; }
    .mark { width: 44px; height: 44px; }
    .headline { font-size: 22px; }
    .checked { order: 3; width: 100%; padding-left: 58px; }
    li.hasfix { flex-wrap: wrap; }
    li.hasfix .what, li.hasfix .lw { flex-basis: 100%; }
    li.hasfix .rowacts { margin-left: auto; }
  }
`;

if (!customElements.get("home-checkup-panel")) customElements.define("home-checkup-panel", HomeCheckupPanel);
