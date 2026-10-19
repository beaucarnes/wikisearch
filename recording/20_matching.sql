SELECT plainto_tsquery('english', 'volcano eruption ash cloud aviation') AS all_terms;
SELECT to_tsvector('english', 'Volcanic ash from an eruption disrupts flights')
  @@ plainto_tsquery('english', 'volcano eruption ash cloud aviation') AS and_match;
SELECT to_tsquery('english', 'volcano | eruption | ash | cloud | aviation') AS any_term;
