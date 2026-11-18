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
    "Offline devices": "Appareils hors ligne",
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
    "Keep": "Garder",
    "Keep means this is fine. It will not show again.": "Garder veut dire que c’est normal. Cela ne s’affichera plus.",
    "Show all {n}": "Tout afficher ({n})",
    "Show fewer": "Afficher moins",
    "Kept. It will not show again.": "Gardé. Cela ne s’affichera plus.",
    "Undo": "Annuler",
    "Kept items ({n})": "Éléments gardés ({n})",
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
    "It did not answer in time. It may be off, busy or far from Wi-Fi.": "Il n’a pas répondu à temps. Il est peut-être éteint, occupé ou loin du Wi-Fi.",
    "Home Assistant could not reach it. Check that it is on and on the network.": "Home Assistant n’a pas pu le joindre. Vérifiez qu’il est allumé et sur le réseau.",
    "Its sign-in no longer works. Open the integration and sign in again.": "Sa connexion ne marche plus. Ouvrez l’intégration et reconnectez-vous.",
    "The service asked Home Assistant to slow down. This usually fixes itself.": "Le service a demandé à Home Assistant de ralentir. Cela se règle souvent tout seul.",
    "A secure connection failed. Check the address and the certificate.": "Une connexion sécurisée a échoué. Vérifiez l’adresse et le certificat.",
    "The device is offline. Check its power and Wi-Fi.": "L’appareil est hors ligne. Vérifiez son alimentation et son Wi-Fi.",
    "It asked for something that does not exist. An update of the integration may fix it.": "Il a demandé quelque chose qui n’existe pas. Une mise à jour de l’intégration peut régler cela.",
    "The integration works in a way Home Assistant warns about. An update usually fixes it.": "L’intégration fonctionne d’une façon que Home Assistant signale. Une mise à jour règle souvent cela.",
    "It uses something Home Assistant will remove. An update usually fixes it.": "Il utilise quelque chose que Home Assistant va retirer. Une mise à jour règle souvent cela.",
    "A template reads something that is missing. Check the template.": "Un modèle lit quelque chose qui manque. Vérifiez le modèle.",
    "Something points to an entity that no longer exists.": "Quelque chose pointe vers une entité qui n’existe plus.",
    "It starts slowly. Usually harmless.": "Il démarre lentement. Souvent sans gravité.",
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
    "See the update": "Voir la mise à jour",
    "Sign in again": "Se reconnecter",
    "Open the devices": "Ouvrir les appareils",
    "Open dashboards": "Ouvrir les tableaux de bord",
    "Open the log": "Ouvrir le journal",
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
    "Offline devices": "Offline-Geräte",
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
    "Keep": "Behalten",
    "Keep means this is fine. It will not show again.": "Behalten heißt: Das ist in Ordnung. Es wird nicht mehr angezeigt.",
    "Show all {n}": "Alle {n} zeigen",
    "Show fewer": "Weniger zeigen",
    "Kept. It will not show again.": "Behalten. Es wird nicht mehr angezeigt.",
    "Undo": "Rückgängig",
    "Kept items ({n})": "Behaltene Einträge ({n})",
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
    "It did not answer in time. It may be off, busy or far from Wi-Fi.": "Es hat nicht rechtzeitig geantwortet. Es ist vielleicht aus, beschäftigt oder weit vom WLAN.",
    "Home Assistant could not reach it. Check that it is on and on the network.": "Home Assistant konnte es nicht erreichen. Prüfen Sie, ob es an und im Netzwerk ist.",
    "Its sign-in no longer works. Open the integration and sign in again.": "Die Anmeldung funktioniert nicht mehr. Öffnen Sie die Integration und melden Sie sich neu an.",
    "The service asked Home Assistant to slow down. This usually fixes itself.": "Der Dienst hat Home Assistant gebeten, langsamer zu machen. Das löst sich meist von selbst.",
    "A secure connection failed. Check the address and the certificate.": "Eine sichere Verbindung ist fehlgeschlagen. Prüfen Sie Adresse und Zertifikat.",
    "The device is offline. Check its power and Wi-Fi.": "Das Gerät ist offline. Prüfen Sie Strom und WLAN.",
    "It asked for something that does not exist. An update of the integration may fix it.": "Es hat etwas angefragt, das es nicht gibt. Ein Update der Integration kann helfen.",
    "The integration works in a way Home Assistant warns about. An update usually fixes it.": "Die Integration arbeitet auf eine Art, vor der Home Assistant warnt. Ein Update hilft meist.",
    "It uses something Home Assistant will remove. An update usually fixes it.": "Es nutzt etwas, das Home Assistant entfernen wird. Ein Update hilft meist.",
    "A template reads something that is missing. Check the template.": "Eine Vorlage liest etwas, das fehlt. Prüfen Sie die Vorlage.",
    "Something points to an entity that no longer exists.": "Etwas verweist auf eine Entität, die es nicht mehr gibt.",
    "It starts slowly. Usually harmless.": "Es startet langsam. Meist harmlos.",
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
    "See the update": "Update ansehen",
    "Sign in again": "Neu anmelden",
    "Open the devices": "Geräte öffnen",
    "Open dashboards": "Dashboards öffnen",
    "Open the log": "Protokoll öffnen",
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
    "Offline devices": "Sin conexión",
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
    "Keep": "Conservar",
    "Keep means this is fine. It will not show again.": "Conservar significa que está bien. No volverá a mostrarse.",
    "Show all {n}": "Mostrar los {n}",
    "Show fewer": "Mostrar menos",
    "Kept. It will not show again.": "Conservado. No volverá a mostrarse.",
    "Undo": "Deshacer",
    "Kept items ({n})": "Elementos conservados ({n})",
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
    "It did not answer in time. It may be off, busy or far from Wi-Fi.": "No respondió a tiempo. Puede estar apagado, ocupado o lejos del Wi-Fi.",
    "Home Assistant could not reach it. Check that it is on and on the network.": "Home Assistant no pudo alcanzarlo. Compruebe que está encendido y en la red.",
    "Its sign-in no longer works. Open the integration and sign in again.": "Su inicio de sesión ya no funciona. Abra la integración e inicie sesión de nuevo.",
    "The service asked Home Assistant to slow down. This usually fixes itself.": "El servicio pidió a Home Assistant ir más despacio. Suele arreglarse solo.",
    "A secure connection failed. Check the address and the certificate.": "Falló una conexión segura. Compruebe la dirección y el certificado.",
    "The device is offline. Check its power and Wi-Fi.": "El dispositivo está sin conexión. Compruebe su corriente y su Wi-Fi.",
    "It asked for something that does not exist. An update of the integration may fix it.": "Pidió algo que no existe. Una actualización de la integración puede arreglarlo.",
    "The integration works in a way Home Assistant warns about. An update usually fixes it.": "La integración funciona de un modo que Home Assistant avisa. Una actualización suele arreglarlo.",
    "It uses something Home Assistant will remove. An update usually fixes it.": "Usa algo que Home Assistant va a quitar. Una actualización suele arreglarlo.",
    "A template reads something that is missing. Check the template.": "Una plantilla lee algo que falta. Revise la plantilla.",
    "Something points to an entity that no longer exists.": "Algo apunta a una entidad que ya no existe.",
    "It starts slowly. Usually harmless.": "Arranca despacio. Suele ser inofensivo.",
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
    "See the update": "Ver la actualización",
    "Sign in again": "Iniciar sesión de nuevo",
    "Open the devices": "Abrir los dispositivos",
    "Open dashboards": "Abrir paneles",
    "Open the log": "Abrir el registro",
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
  ["Offline devices", ["unavailable"]],
  ["Helpers", ["unused_helpers"]],
  ["Batteries", ["low_batteries"]],
];

/** What a log error means, by the code Home Checkup gives it. */
const MEANINGS = {
  timeout: "It did not answer in time. It may be off, busy or far from Wi-Fi.",
  unreachable: "Home Assistant could not reach it. Check that it is on and on the network.",
  signin: "Its sign-in no longer works. Open the integration and sign in again.",
  slowdown: "The service asked Home Assistant to slow down. This usually fixes itself.",
  certificate: "A secure connection failed. Check the address and the certificate.",
  offline: "The device is offline. Check its power and Wi-Fi.",
  notfound: "It asked for something that does not exist. An update of the integration may fix it.",
  blocking: "The integration works in a way Home Assistant warns about. An update usually fixes it.",
  deprecated: "It uses something Home Assistant will remove. An update usually fixes it.",
  template: "A template reads something that is missing. Check the template.",
  missing: "Something points to an entity that no longer exists.",
  slowstart: "It starts slowly. Usually harmless.",
  database: "The history database had a problem. Your history may have a gap.",
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
  update: ["An update is ready ({version}). Updates often fix errors like these.", "See the update"],
  signin: ["", "Sign in again"],
  devices: ["", "Open the devices"],
  template: ["", "Open dashboards"],
  logs: ["", "Open the log"],
};

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

class HomeCheckupPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._report = null;
    this._error = "";
    this._open = new Set();
    this._scanning = false;
    this._toast = null;
    this._keptOpen = false;
    this._sheet = null;
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
    this._say(keep ? { text: this._t("Kept. It will not show again."), act: "undo", data: key } : null);
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

  async _undoFix(id) {
    const fix = (this._report?.fixes || []).find((f) => f.id === id);
    if (!fix || this._undoing) return;
    this._undoing = id;
    this._render();
    try {
      let result;
      if (fix.kind === "leftover_entities") {
        result = await this._hass.callWS({ type: "home_checkup/fix_undo", fix_id: id });
      } else if (fix.kind === "use_new" || fix.kind === "remove_step" || fix.kind === "turn_off") {
        const saved = await this._hass.callWS({ type: "home_checkup/fix_automation_saved", fix_id: id });
        if (fix.kind === "turn_off") {
          await this._hass.callService("automation", "turn_on", { entity_id: saved.automation });
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
            : f.kind === "use_new"
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
    const warnings = findings.filter((f) => f.severity === "warning");
    const notes = findings.filter((f) => f.severity !== "warning");
    const level = r.count ? "warn" : "good";
    const checked = r.scanned_at ? this._t("Checked {time}", { time: this._time(r.scanned_at) }) : this._t("Not checked yet");

    const chips = CHECKS.map(([label, kinds]) => {
      const mine = findings.filter((f) => kinds.includes(f.kind));
      const state = mine.some((f) => f.severity === "warning") ? "warn" : mine.length ? "note" : "fine";
      const icon =
        state === "fine"
          ? `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>`
          : `<span class="dot"></span>`;
      return `<span class="chip ${state}">${icon}${esc(this._t(label))}</span>`;
    }).join("");

    const kept = r.kept ?? [];
    let html = `
      <div class="hero ${level}">
        ${mark(level)}
        <div class="words">
          <div class="headline">${esc(this._headline(r.count ?? 0))}</div>
          <div class="detail">${esc(r.count ? this._t("Nothing changes until you choose to.") : this._t("Nothing needs a look today."))}</div>
        </div>
        <div class="checked">${esc(checked)}</div>
      </div>
      <div class="chips">${chips}</div>`;
    if (findings.length) html += `<div class="keephint">${esc(this._t("Keep means this is fine. It will not show again."))}</div>`;
    if (warnings.length) html += `<div class="grid">${warnings.map((f) => this._finding(f, false)).join("")}</div>`;
    if (notes.length) {
      html += `<div class="section">${esc(this._t("Good to know"))}</div><div class="grid">${notes.map((f) => this._finding(f, true)).join("")}</div>`;
    }
    html += this._fixesHtml(r.fixes ?? []);
    if (kept.length) {
      html += `<button class="keptbar" type="button" data-act="kept">${esc(this._t("Kept items ({n})", { n: kept.length }))}<svg viewBox="0 0 24 24" class="${this._keptOpen ? "up" : ""}" aria-hidden="true"><path d="M7 10l5 5 5-5"/></svg></button>`;
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
    return html;
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
        const mean = it.hint && MEANINGS[it.hint] ? `<span class="mean">${esc(this._t(MEANINGS[it.hint]))}</span>` : "";
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
        const info = (infoText ? `<span class="info">${esc(infoText)}</span>` : "") + mean;
        const label = it.link
          ? `<a class="what" href="${esc(it.link)}" data-act="go" data-link="${esc(it.link)}">${name}${info}</a>`
          : `<span class="what">${name}${info}</span>`;
        const fixLabel = it.fix === "use_new" ? "Use the new one" : it.fix === "remove_step" ? "Remove this step" : it.fix === "turn_off" ? "Turn off" : "";
        const fixBtn = fixLabel
          ? `<button type="button" class="fixbtn" data-act="autofix" data-key="${esc(it.key)}" ${this._fixing ? "disabled" : ""}>${esc(this._fixing === it.key ? "…" : this._t(fixLabel))}</button>`
          : "";
        return `<li class="${fixBtn ? "hasfix" : ""}">${label}<span class="rowacts">${fixBtn}<button type="button" class="ghost" data-act="keep" data-key="${esc(it.key)}">${esc(this._t("Keep"))}</button></span></li>`;
      })
      .join("");
    const more =
      items.length > SHOWN
        ? `<button type="button" class="more" data-act="more" data-id="${esc(id)}">${esc(open ? this._t("Show fewer") : this._t("Show all {n}", { n: items.length }))}</button>`
        : "";
    const step = STEPS[f.action];
    let openLink = f.link
      ? `<a class="open" href="${esc(f.link)}" data-act="go" data-link="${esc(f.link)}">${esc(this._t("Open"))}</a>`
      : "";
    if (step && f.kind === "log_errors") {
      const label = f.action === "template" && !f.action_link.startsWith("/config/lovelace") ? "Open" : step[1];
      openLink = `<a class="open stepbtn" href="${esc(f.action_link)}" data-act="step" data-link="${esc(f.action_link)}" data-key="${esc(f.integration ?? "")}" data-step="${esc(f.action)}">${esc(this._t(label))}</a>`;
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
      <section class="finding ${note ? "note" : ""}">
        <div class="head">
          <div class="htext"><div class="title">${esc(this._title(f))}</div>${hint ? `<div class="hint">${esc(hint)}</div>` : ""}</div>
          <div class="acts">${fixButton}${openLink}</div>
        </div>
        ${stepLine}
        ${rows && f.kind !== "log_stopped" ? `<ul class="${isLog ? "log" : ""}">${rows}</ul>` : ""}
        ${more}
      </section>`;
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
  .content { flex: 1; overflow-y: auto; padding: 24px 24px 48px; box-sizing: border-box; width: 100%; max-width: 1120px; margin: 0 auto;
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
  .keephint { font-size: 13px; color: var(--dim); }

  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 440px), 1fr)); gap: 16px; align-items: start; }
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
  .open { font-size: 14px; font-weight: 500; color: var(--primary-color); text-decoration: none; padding: 4px 2px; white-space: nowrap; }
  ul { list-style: none; margin: 10px 0 0; padding: 0; }
  li { display: flex; align-items: center; gap: 8px; padding: 6px 0; border-top: 1px solid var(--line); min-height: 36px; }
  .what { flex: 1; min-width: 0; display: flex; flex-direction: column; color: inherit; text-decoration: none; font-size: 15px; }
  a.what:hover .nm { color: var(--primary-color); }
  .nm { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .to, .info { color: var(--dim); }
  .info { font-size: 13px; }
  .mean { font-size: 13px; color: var(--primary-text-color); margin-top: 2px; }
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
    li.hasfix .what { flex-basis: 100%; }
    li.hasfix .rowacts { margin-left: auto; }
  }
`;

if (!customElements.get("home-checkup-panel")) customElements.define("home-checkup-panel", HomeCheckupPanel);
