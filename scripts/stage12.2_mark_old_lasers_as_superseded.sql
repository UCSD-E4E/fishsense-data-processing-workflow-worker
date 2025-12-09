UPDATE laserlabel
SET superseded = true
FROM specieslabel
JOIN image ON specieslabel.image_id = image.id
JOIN dive ON dive.id = image.dive_id
WHERE laserlabel.image_id = specieslabel.image_id
AND image.is_canonical = true
AND specieslabel.label_studio_task_id != laserlabel.label_studio_task_id
AND dive.id = 383