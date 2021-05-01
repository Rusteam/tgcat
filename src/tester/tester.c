#ifdef NDEBUG
#undef NDEBUG
#endif

#include "json.h"
#include "json-builder.h"
#include "tgcat.h"

#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#if defined(_WIN32)
#include "windows.h"
#endif

#define MAX_POSTS 100
#define MAX_TEST_LENGTH 1000000

/**
 * Names of supported categories.
 */
static const char *TGCAT_CATEGORY_NAME[] = {
  "Art & Design",
  "Bets & Gambling",
  "Books",
  "Business & Entrepreneurship",
  "Cars & Other Vehicles",
  "Celebrities & Lifestyle",
  "Cryptocurrencies",
  "Culture & Events",
  "Curious Facts",
  "Directories of Channels & Bots",
  "Drug Sale",
  "Economy & Finance",
  "Education",
  "Erotic Content",
  "Fashion & Beauty",
  "Fitness",
  "Food & Cooking",
  "Foreign Language Learning",
  "Forgery",
  "Hacked Accounts & Software",
  "Health & Medicine",
  "History",
  "Hobbies & Activities",
  "Home & Architecture",
  "Humor & Memes",
  "Investments",
  "Job Listings",
  "Kids & Parenting",
  "Marketing & PR",
  "Motivation & Self-development",
  "Movies",
  "Music",
  "Offers & Promotions",
  "Personal Data",
  "Pets",
  "Pirated Content",
  "Politics & Incidents",
  "Prostitution",
  "Psychology & Relationships",
  "Real Estate",
  "Recreation & Entertainment",
  "Religion & Spirituality",
  "Science",
  "Spam & Fake Followers",
  "Sports",
  "Technology & Internet",
  "Travel & Tourism",
  "Video Games",
  "Weapon Sale",
  "Other"
};

static struct TelegramLinkPreview link_previews[MAX_POSTS];
static struct TelegramChannelPost posts[MAX_POSTS];

static char buf[MAX_TEST_LENGTH];

static double category_probability[TGCAT_CATEGORY_OTHER + 1];

static double get_monotonic_time() {
#if defined(_WIN32)
  LARGE_INTEGER frequency;
  LARGE_INTEGER count;
  int success = QueryPerformanceFrequency(&frequency) != 0 && QueryPerformanceCounter(&count) != 0;
  assert(success);
  return (double)count.QuadPart / (double)frequency.QuadPart;
#else
  struct timespec ts;
  int err = clock_gettime(CLOCK_MONOTONIC, &ts);
  assert(err == 0);
  return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
#endif
}

static int init_counters(struct TelegramChannelInfo *info, json_value *value) {
  if (value->type != json_object) {
    fprintf(stderr, "Field \"counters\" has wrong type\n");
    return -1;
  }

  info->total_post_count = 0;
  info->photo_count = 0;
  info->video_count = 0;
  info->music_count = 0;
  info->file_count = 0;

  size_t i;
  for (i = 0; i < value->u.object.length; i++) {
    const char *field_name = value->u.object.values[i].name;
    json_value *field_value = value->u.object.values[i].value;

    if (strcmp(field_name, "posts") == 0) {
      if (field_value->type != json_integer) {
        fprintf(stderr, "Field \"posts\" has wrong type\n");
        return -1;
      }
      info->total_post_count = (size_t)field_value->u.integer;
    } else if (strcmp(field_name, "photos") == 0) {
      if (field_value->type != json_integer) {
        fprintf(stderr, "Field \"photos\" has wrong type\n");
        return -1;
      }
      info->photo_count = (size_t)field_value->u.integer;
    } else if (strcmp(field_name, "videos") == 0) {
      if (field_value->type != json_integer) {
        fprintf(stderr, "Field \"videos\" has wrong type\n");
        return -1;
      }
      info->video_count = (size_t)field_value->u.integer;
    } else if (strcmp(field_name, "audios") == 0) {
      if (field_value->type != json_integer) {
        fprintf(stderr, "Field \"audios\" has wrong type\n");
        return -1;
      }
      info->music_count = (size_t)field_value->u.integer;
    } else if (strcmp(field_name, "files") == 0) {
      if (field_value->type != json_integer) {
        fprintf(stderr, "Field \"files\" has wrong type\n");
        return -1;
      }
      info->file_count = (size_t)field_value->u.integer;
    } else {
      fprintf(stderr, "Unknown counter \"%s\" found\n", field_name);
      return -1;
    }
  }
  return 0;
}

static int init_link_preview(struct TelegramLinkPreview *link_preview, json_value *value) {
  if (value->type != json_object) {
    fprintf(stderr, "Post expected to be an object\n");
    return -1;
  }

  int field_mask = 0;
  size_t i;
  for (i = 0; i < value->u.object.length; i++) {
    const char *field_name = value->u.object.values[i].name;
    json_value *field_value = value->u.object.values[i].value;

    if (strcmp(field_name, "url") == 0) {
      field_mask |= 1 << 0;
      if (field_value->type != json_string) {
        fprintf(stderr, "Field \"url\" has wrong type\n");
        return -1;
      }
      link_preview->url = field_value->u.string.ptr;
    } else if (strcmp(field_name, "title") == 0) {
      field_mask |= 1 << 1;
      if (field_value->type != json_string) {
        fprintf(stderr, "Field \"title\" has wrong type\n");
        return -1;
      }
      link_preview->title = field_value->u.string.ptr;
    } else if (strcmp(field_name, "description") == 0) {
      field_mask |= 1 << 2;
      if (field_value->type != json_string) {
        fprintf(stderr, "Field \"description\" has wrong type\n");
        return -1;
      }
      link_preview->description = field_value->u.string.ptr;
    } else {
      fprintf(stderr, "Unknown field \"%s\" found\n", field_name);
      return -1;
    }
  }

  if (field_mask != (1 << 3) - 1) {
    fprintf(stderr, "Some link preview fields are missing\n");
    return -1;
  }

  return 0;
}

static int init_post(struct TelegramChannelPost *post, struct TelegramLinkPreview *link_preview, json_value *value) {
  if (value->type != json_object) {
    fprintf(stderr, "Post expected to be an object\n");
    return -1;
  }

  post->type = TELEGRAM_CHANNEL_POST_TYPE_TEXT;
  post->link_preview = NULL;
  post->duration = 0;
  post->file_name = NULL;
  post->file_size = 0;
  post->music_performer = NULL;
  post->music_title = NULL;

  int field_mask = 0;
  size_t i;
  for (i = 0; i < value->u.object.length; i++) {
    const char *field_name = value->u.object.values[i].name;
    json_value *field_value = value->u.object.values[i].value;

    if (strcmp(field_name, "type") == 0) {
      field_mask |= 1 << 0;
      if (field_value->type != json_string) {
        fprintf(stderr, "Field \"type\" has wrong type\n");
        return -1;
      }

      const char *type = field_value->u.string.ptr;
      if (strcmp(type, "text") == 0) {
        post->type = TELEGRAM_CHANNEL_POST_TYPE_TEXT;
      } else if (strcmp(type, "photo") == 0) {
        post->type = TELEGRAM_CHANNEL_POST_TYPE_PHOTO;
      } else if (strcmp(type, "video") == 0) {
        post->type = TELEGRAM_CHANNEL_POST_TYPE_VIDEO;
      } else if (strcmp(type, "audio") == 0) {
        post->type = TELEGRAM_CHANNEL_POST_TYPE_MUSIC;
      } else if (strcmp(type, "file") == 0) {
        post->type = TELEGRAM_CHANNEL_POST_TYPE_FILE;
      } else {
        fprintf(stderr, "Receive unsupported post type \"%s\"\n", type);
        return -1;
      }
    } else if (strcmp(field_name, "text") == 0) {
      field_mask |= 1 << 1;
      if (field_value->type != json_string) {
        fprintf(stderr, "Field \"text\" has wrong type\n");
        return -1;
      }
      post->text = field_value->u.string.ptr;
    } else if (strcmp(field_name, "file_size") == 0) {
      field_mask |= 1 << 2;
      if (field_value->type != json_integer) {
        fprintf(stderr, "Field \"file_size\" has wrong type\n");
        return -1;
      }
      post->file_size = (size_t)field_value->u.integer;
    } else if (strcmp(field_name, "file_name") == 0) {
      field_mask |= 1 << 3;
      if (field_value->type != json_string) {
        fprintf(stderr, "Field \"file_name\" has wrong type\n");
        return -1;
      }
      post->file_name = field_value->u.string.ptr;
    } else if (strcmp(field_name, "duration") == 0) {
      if (field_value->type != json_integer || field_value->u.integer < 0 || field_value->u.integer > INT_MAX) {
        fprintf(stderr, "Field \"duration\" has wrong type\n");
        return -1;
      }
      post->duration = (size_t)field_value->u.integer;
    } else if (strcmp(field_name, "performer") == 0) {
      field_mask |= 1 << 4;
      if (field_value->type != json_string) {
        fprintf(stderr, "Field \"performer\" has wrong type\n");
        return -1;
      }
      post->music_performer = field_value->u.string.ptr;
    } else if (strcmp(field_name, "title") == 0) {
      field_mask |= 1 << 5;
      if (field_value->type != json_string) {
        fprintf(stderr, "Field \"title\" has wrong type\n");
        return -1;
      }
      post->music_title = field_value->u.string.ptr;
    } else if (strcmp(field_name, "link_preview") == 0) {
      if (init_link_preview(link_preview, field_value) < 0) {
        return -1;
      }
      post->link_preview = link_preview;
    } else {
      fprintf(stderr, "Unknown field \"%s\" found\n", field_name);
      return -1;
    }
  }

  const int expected_field_mask[] = {3, 3, 15, 15 | 16 | 32, 15};
  if ((expected_field_mask[post->type] & (1 << 3)) && (field_mask & (1 << 3)) == 0) {
    field_mask |= 1 << 3;
    post->file_name = "";
  }
  if ((expected_field_mask[post->type] & (1 << 4)) && (field_mask & (1 << 4)) == 0) {
    field_mask |= 1 << 4;
    post->music_performer = "";
  }
  if ((expected_field_mask[post->type] & (1 << 5)) && (field_mask & (1 << 5)) == 0) {
    field_mask |= 1 << 5;
    post->music_title = "";
  }
  if (field_mask != expected_field_mask[post->type]) {
    fprintf(stderr, "Have field mask %d instead of expected mask %d in a post of the type %d\n", field_mask,
            expected_field_mask[post->type], post->type);
    return -1;
  }

  return 0;
}

int main(int argc, char **argv) {
  if (argc != 4) {
    fprintf(stderr, "Usage: tgcat-tester <mode> <input_file> <output_file>\n");
    return 1;
  }

  // read <mode> command-line argument
  enum mode_t { LANGUAGE, CATEGORY } mode;
  if (strcmp(argv[1], "language") == 0) {
    mode = LANGUAGE;
  } else if (strcmp(argv[1], "category") == 0) {
    mode = CATEGORY;
  } else {
    fprintf(stderr, "Unsupported mode \"%s\" specified\n", argv[1]);
    return 1;
  }

  // read <input_file> command-line argument
  FILE *in = fopen(argv[2], "r");
  if (in == NULL) {
    fprintf(stderr, "Failed to open input file %s\n", argv[2]);
    return 1;
  }

  // read <output_file> command-line argument
  FILE *out = fopen(argv[3], "w");
  if (out == NULL) {
    fprintf(stderr, "Failed to open output file %s\n", argv[3]);
    return 1;
  }

  // query
  struct TelegramChannelInfo info;
  info.recent_posts = posts;

  // json serialization options
  json_serialize_opts options;
  options.mode = json_serialize_mode_packed;
  options.opts = 0;
  options.indent_size = 0;

  // statistics
  double execution_time = 0.0;
  int query_count = 0;

  // initialize library
  if (tgcat_init() != 0) {
    fprintf(stderr, "Failed to init tgcat library\n");
    return 0;
  }

  while (!ferror(in) && !feof(in)) {
    char *fgets_result = fgets(buf, sizeof(buf), in);
    if (fgets_result == NULL) {
      break;
    }
    if (ferror(in)) {
      fprintf(stderr, "Failed to read input file %s\n", argv[2]);
      return 1;
    }

    size_t len = strlen(buf);
    assert(len > 0);

    if (buf[len - 1] != '\n') {
      fprintf(stderr, "Input file contains too big test string\n");
      return 1;
    }

    buf[--len] = '\0';

    if (len == 0) {
      fputs("\n", out);
      continue;
    }

    json_value *value = json_parse((json_char *)buf, len);
    if (value == NULL || value->type != json_object || value->u.object.length != 5) {
      fprintf(stderr, "Failed to parse input string as JSON object\n");
      return 1;
    }

    int field_mask = 0;
    size_t i;
    for (i = 0; i < value->u.object.length; i++) {
      const char *field_name = value->u.object.values[i].name;
      json_value *field_value = value->u.object.values[i].value;

      if (strcmp(field_name, "title") == 0) {
        field_mask |= 1 << 0;
        if (field_value->type != json_string) {
          fprintf(stderr, "Field \"title\" has wrong type\n");
          return 1;
        }
        info.title = field_value->u.string.ptr;
      } else if (strcmp(field_name, "description") == 0) {
        field_mask |= 1 << 1;
        if (field_value->type != json_string) {
          fprintf(stderr, "Field \"description\" has wrong type\n");
          return 1;
        }
        info.description = field_value->u.string.ptr;
      } else if (strcmp(field_name, "recent_posts") == 0) {
        field_mask |= 1 << 2;
        if (field_value->type != json_array) {
          fprintf(stderr, "Field \"recent_posts\" has wrong type\n");
          return 1;
        }
        if (field_value->u.array.length > MAX_POSTS) {
          fprintf(stderr, "Too much posts available\n");
          return 1;
        }
        info.recent_post_count = field_value->u.array.length;
        size_t j;
        for (j = 0; j < info.recent_post_count; j++) {
          if (init_post(&info.recent_posts[j], &link_previews[j], field_value->u.array.values[j]) < 0) {
            return 1;
          }
        }
      } else if (strcmp(field_name, "subscribers") == 0) {
        field_mask |= 1 << 3;
        if (field_value->type != json_integer) {
          fprintf(stderr, "Field \"subscribers\" has wrong type\n");
          return 1;
        }
        info.subscriber_count = (size_t)field_value->u.integer;
      } else if (strcmp(field_name, "counters") == 0) {
        field_mask |= 1 << 4;
        if (init_counters(&info, field_value) < 0) {
          return 1;
        }
      } else {
        fprintf(stderr, "Unknown field \"%s\" found\n", field_name);
        return 1;
      }
    }
    if (field_mask != (1 << 5) - 1) {
      fprintf(stderr, "Some input fields are missing\n");
      return 1;
    }

    json_value *result = json_object_new(2);
    assert(result != NULL);

    query_count++;
    execution_time -= get_monotonic_time();

    if (mode == LANGUAGE || mode == CATEGORY) {
      char language_code[6] = {0};
      if (tgcat_detect_language(&info, language_code) == 0) {
        json_value *push_result = json_object_push(result, "lang_code", json_string_new(language_code));
        assert(push_result != NULL);
      }
    }

    if (mode == CATEGORY) {
      memset(category_probability, 0, sizeof(category_probability));
      if (tgcat_detect_category(&info, category_probability) == 0) {
        json_value *category = json_object_new(2);
        assert(category != NULL);

        int index;
        for (index = 0; index <= TGCAT_CATEGORY_OTHER; index++) {
          if (0.0 < category_probability[index] && category_probability[index] <= 1.0) {
            json_value *push_result =
                json_object_push(category, TGCAT_CATEGORY_NAME[index], json_double_new(category_probability[index]));
            assert(push_result != NULL);
          }
        }

        json_value *push_result = json_object_push(result, "category", category);
        assert(push_result != NULL);
      }
    }

    execution_time += get_monotonic_time();

    json_serialize_ex(buf, result, options);

    fputs(buf, out);
    fputs("\n", out);

    json_builder_free(result);

    json_value_free(value);
  }

  printf("Processed %d queries in %.6lf seconds\n", query_count, execution_time);
}
